from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.audit import AuditLog
from app.security.auth import get_current_user
from app.security.abac_policy import ABACPolicyEngine, FieldAction
from app.security.exposure_engine import ExposureEngine
from app.security.schemas import (
    CustomerSummary,
    CustomerDetailResponse,
    AccessRequest,
    TransactionDetail,
    AccessAuditMeta
)
from app.crypto.aes_cipher import vault_cipher
from app.crypto.masking import DataMasker

router = APIRouter(prefix="/customers", tags=["Customers & Vault Access"])

class BulkExportRequest(BaseModel):
    customer_ids: List[int]
    format: str = "CSV"
    purpose: str

@router.get("", response_model=List[CustomerSummary])
def list_customers(
    q: Optional[str] = Query(None, description="Search by customer name, email, or code"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search and browse customers.
    Returns safe, privacy-masked previews. Never reveals plaintext PAN or unmasked account numbers.
    """
    query = db.query(Customer)
    if q:
        search_filter = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Customer.full_name.ilike(search_filter),
                Customer.email.ilike(search_filter),
                Customer.customer_code.ilike(search_filter)
            )
        )
    
    customers = query.limit(limit).all()
    
    results = []
    for c in customers:
        try:
            raw_acc = vault_cipher.decrypt(c.account_number_enc, c.account_number_nonce, associated_data=c.customer_code)
            masked_acc = DataMasker.mask_account_number(raw_acc)
        except Exception:
            masked_acc = "•••• •••• ••••"

        results.append(
            CustomerSummary(
                id=c.id,
                customer_code=c.customer_code,
                full_name=c.full_name,
                email=c.email,
                phone_masked=DataMasker.mask_phone(c.phone),
                account_number_masked=masked_acc,
                kyc_status=c.kyc_status,
                risk_tier=c.risk_tier
            )
        )
    return results

@router.get("/purposes")
def get_available_purposes(role: str = Query("SUPPORT", description="Employee role")):
    """Returns valid business purposes authorized for the specified role."""
    return ABACPolicyEngine.list_available_purposes(role)

@router.post("/{customer_id}/access", response_model=CustomerDetailResponse)
def request_customer_access(
    customer_id: int,
    access_req: AccessRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Context-Aware Purpose-Based Disclosure Endpoint with Adaptive Exposure Budgeting.
    1. Evaluates ABAC Policy (Role + Purpose).
    2. Validates & Charges Exposure Points (Locks session if quota breached).
    3. Decrypts or masks fields dynamically based on policy.
    4. Writes tamper-evident audit record.
    """
    # Resolve current user from JWT header or fallback to requested username
    auth_header = request.headers.get("Authorization")
    current_user = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            current_user = get_current_user(token=token, db=db)
        except Exception:
            current_user = None

    if not current_user:
        target_name = access_req.username or "support_alice"
        current_user = db.query(User).filter(User.username == target_name).first()
        if not current_user:
            current_user = db.query(User).first()
    # 1. Lookup Customer
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer record not found")

    # 2. Evaluate Context-Aware ABAC Policy
    decision = ABACPolicyEngine.evaluate(
        user_role=current_user.role,
        purpose_key=access_req.purpose,
        ticket_id=access_req.ticket_id
    )

    # 3. Handle Unauthorized Purpose Access
    if not decision.is_allowed:
        denied_log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            role=current_user.role,
            customer_id=customer.id,
            customer_code=customer.customer_code,
            purpose=access_req.purpose,
            ticket_id=access_req.ticket_id,
            accessed_fields="NONE",
            action_type="ACCESS_DENIED",
            exposure_points=0,
            risk_score=0.8,
            status="DENIED"
        )
        db.add(denied_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=decision.denial_reason
        )

    # 4. Enforce Adaptive Exposure Budget
    is_budget_ok, budget_err = ExposureEngine.check_and_charge_exposure(
        db=db,
        user=current_user,
        points=decision.exposure_points,
        customer_code=customer.customer_code
    )

    if not is_budget_ok:
        # Record budget lock in audit log
        budget_blocked_log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            role=current_user.role,
            customer_id=customer.id,
            customer_code=customer.customer_code,
            purpose=decision.purpose,
            ticket_id=access_req.ticket_id,
            accessed_fields="NONE",
            action_type="EXPOSURE_BUDGET_LOCKED",
            exposure_points=decision.exposure_points,
            risk_score=0.95,
            status="THROTTLED"
        )
        db.add(budget_blocked_log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=budget_err
        )

    # 5. Process Fields According to ABAC Actions (DECRYPTED vs MASKED vs REDACTED)
    field_actions = decision.field_actions
    disclosed_fields = []
    masked_fields = []
    redacted_fields = []

    code = customer.customer_code
    raw_acc = vault_cipher.decrypt(customer.account_number_enc, customer.account_number_nonce, associated_data=code)
    raw_pan = vault_cipher.decrypt(customer.pan_enc, customer.pan_nonce, associated_data=code)
    raw_bal = vault_cipher.decrypt(customer.balance_enc, customer.balance_nonce, associated_data=code)

    # Evaluate Account Number
    if field_actions.get("account_number") == FieldAction.DECRYPTED:
        final_acc = raw_acc
        disclosed_fields.append("account_number")
    elif field_actions.get("account_number") == FieldAction.MASKED:
        final_acc = DataMasker.mask_account_number(raw_acc)
        masked_fields.append("account_number")
    else:
        final_acc = DataMasker.redact("account_number")
        redacted_fields.append("account_number")

    # Evaluate PAN Card
    if field_actions.get("pan") == FieldAction.DECRYPTED:
        final_pan = raw_pan
        disclosed_fields.append("pan")
    elif field_actions.get("pan") == FieldAction.MASKED:
        final_pan = DataMasker.mask_pan(raw_pan)
        masked_fields.append("pan")
    else:
        final_pan = DataMasker.redact("pan")
        redacted_fields.append("pan")

    # Evaluate Balance
    if field_actions.get("balance") == FieldAction.DECRYPTED:
        final_bal = f"₹ {float(raw_bal):,.2f}"
        disclosed_fields.append("balance")
    elif field_actions.get("balance") == FieldAction.MASKED:
        final_bal = DataMasker.mask_balance(raw_bal)
        masked_fields.append("balance")
    else:
        final_bal = DataMasker.redact("balance")
        redacted_fields.append("balance")

    # Evaluate Phone
    if field_actions.get("phone") == FieldAction.PLAIN:
        final_phone = customer.phone
        disclosed_fields.append("phone")
    else:
        final_phone = DataMasker.mask_phone(customer.phone)
        masked_fields.append("phone")

    # Evaluate Credit Score
    if field_actions.get("credit_score") == FieldAction.PLAIN:
        final_score = customer.credit_score
        disclosed_fields.append("credit_score")
    else:
        final_score = None
        redacted_fields.append("credit_score")

    # Evaluate Transactions
    tx_list: List[TransactionDetail] = []
    if field_actions.get("transactions") == FieldAction.DECRYPTED:
        disclosed_fields.append("transactions")
        db_txs = db.query(Transaction).filter(Transaction.customer_id == customer.id).all()
        for idx, t in enumerate(db_txs, start=1):
            try:
                tx_amt_raw = vault_cipher.decrypt(t.amount_enc, t.amount_nonce, associated_data=f"{code}-TX-{idx}")
                display_amt = f"₹ {float(tx_amt_raw):,.2f}"
            except Exception:
                display_amt = "₹ [ENCRYPTED]"
            
            tx_list.append(
                TransactionDetail(
                    id=t.id,
                    tx_code=t.tx_code,
                    merchant=t.merchant,
                    category=t.category,
                    amount=display_amt,
                    status=t.status,
                    timestamp=t.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                )
            )
    else:
        redacted_fields.append("transactions")

    # 6. Record Granted Access in Audit Log
    audit_entry = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        customer_id=customer.id,
        customer_code=customer.customer_code,
        purpose=decision.purpose,
        ticket_id=access_req.ticket_id,
        accessed_fields=", ".join(disclosed_fields) if disclosed_fields else "NONE",
        action_type="VIEW_PURPOSE_BASED",
        exposure_points=decision.exposure_points,
        risk_score=0.1,
        status="GRANTED"
    )
    db.add(audit_entry)
    db.commit()

    return CustomerDetailResponse(
        id=customer.id,
        customer_code=customer.customer_code,
        full_name=customer.full_name,
        email=customer.email,
        phone=final_phone,
        account_number=final_acc,
        pan=final_pan,
        balance=final_bal,
        credit_score=final_score,
        kyc_status=customer.kyc_status,
        risk_tier=customer.risk_tier,
        transactions=tx_list,
        access_meta=AccessAuditMeta(
            purpose=decision.purpose,
            exposure_points_charged=decision.exposure_points,
            fields_disclosed=disclosed_fields,
            fields_masked=masked_fields,
            fields_redacted=redacted_fields
        )
    )

@router.post("/export")
def export_customer_records(
    req: BulkExportRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Export Customer Records with Exfiltration Detection.
    If an employee tries to bulk export >10 records without Compliance/Admin authority,
    the request is blocked and flagged as a critical security incident.
    """
    auth_header = request.headers.get("Authorization")
    current_user = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            current_user = get_current_user(token=token, db=db)
        except Exception:
            current_user = None

    if not current_user:
        current_user = db.query(User).filter(User.username == "loan_bob").first()
        if not current_user:
            current_user = db.query(User).first()
    count = len(req.customer_ids)
    is_allowed, denial_reason = ExposureEngine.evaluate_bulk_export(
        db=db,
        user=current_user,
        record_count=count,
        purpose=req.purpose
    )

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=denial_reason
        )

    # If allowed, fetch requested records
    customers = db.query(Customer).filter(Customer.id.in_(req.customer_ids)).all()
    exported_data = []
    for c in customers:
        exported_data.append({
            "customer_code": c.customer_code,
            "full_name": c.full_name,
            "email": c.email,
            "phone": c.phone,
            "kyc_status": c.kyc_status,
            "risk_tier": c.risk_tier
        })

    # Log compliant export
    audit = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        purpose=req.purpose,
        accessed_fields="BULK_METADATA_EXPORT",
        action_type="EXPORT",
        exposure_points=15,
        risk_score=0.4,
        status="GRANTED"
    )
    db.add(audit)
    db.commit()

    return {
        "status": "success",
        "exported_records_count": len(exported_data),
        "data": exported_data
    }
