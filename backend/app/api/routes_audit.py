from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.audit import AuditLog, SecurityIncident
from app.security.auth import get_current_user
from app.security.exposure_engine import ExposureEngine

router = APIRouter(prefix="/audit", tags=["Audit & Security Monitoring"])

@router.get("/exposure/status")
def get_my_exposure_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the real-time session exposure budget status for the active employee.
    Used by the frontend to render the dynamic exposure gauge.
    """
    session_tracker = ExposureEngine.get_or_create_session(db, current_user)
    pct = round((session_tracker.points_used / session_tracker.max_budget) * 100, 1)
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "points_used": session_tracker.points_used,
        "max_budget": session_tracker.max_budget,
        "percentage_used": pct,
        "is_locked": session_tracker.is_locked,
        "lock_reason": session_tracker.lock_reason,
        "records_accessed_count": session_tracker.records_accessed_count
    }

@router.post("/exposure/reset/{target_user_id}")
def reset_employee_session(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supervisor / Admin Override:
    Allows security administrators or compliance officers to review and unlock an employee's session.
    """
    if current_user.role not in {"ADMIN", "COMPLIANCE_AUDITOR"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrators or Compliance Auditors can reset exposure budgets."
        )

    success = ExposureEngine.reset_user_session(db, target_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session tracker not found for specified user")

    # Log supervisor override
    audit = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        purpose="SECURITY_OVERRIDE",
        accessed_fields="EXPOSURE_BUDGET_RESET",
        action_type="ADMIN_UNLOCK",
        exposure_points=0,
        risk_score=0.2,
        status="GRANTED"
    )
    db.add(audit)
    db.commit()

    return {"status": "success", "message": f"Session exposure budget reset for user {target_user_id}"}

@router.get("/logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    username: Optional[str] = None,
    purpose: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns historical compliance audit logs.
    Restricted to Compliance Auditors, Administrators, or personal records for standard employees.
    """
    query = db.query(AuditLog)

    # Standard employees can only view their own logs; Auditors and Admins see everything
    if current_user.role not in {"ADMIN", "COMPLIANCE_AUDITOR"}:
        query = query.filter(AuditLog.user_id == current_user.id)
    elif username:
        query = query.filter(AuditLog.username.ilike(f"%{username}%"))

    if purpose:
        query = query.filter(AuditLog.purpose == purpose.upper())
    if status_filter:
        query = query.filter(AuditLog.status == status_filter.upper())

    total = query.count()
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "username": log.username,
                "role": log.role,
                "customer_code": log.customer_code,
                "purpose": log.purpose,
                "ticket_id": log.ticket_id,
                "accessed_fields": log.accessed_fields,
                "action_type": log.action_type,
                "exposure_points": log.exposure_points,
                "risk_score": log.risk_score,
                "status": log.status
            }
            for log in logs
        ]
    }

@router.get("/incidents")
def get_security_incidents(
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Real-time security incident alert feed.
    Powers the live security operations console on the Admin Dashboard.
    """
    if current_user.role not in {"ADMIN", "COMPLIANCE_AUDITOR"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to Security Administrators and Compliance Auditors."
        )

    query = db.query(SecurityIncident)
    if severity:
        query = query.filter(SecurityIncident.severity == severity.upper())

    incidents = query.order_by(SecurityIncident.timestamp.desc()).limit(limit).all()

    return [
        {
            "id": inc.id,
            "timestamp": inc.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "username": inc.username,
            "incident_type": inc.incident_type,
            "severity": inc.severity,
            "description": inc.description,
            "blocked": inc.blocked,
            "ip_address": inc.ip_address
        }
        for inc in incidents
    ]

