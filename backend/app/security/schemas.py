from typing import List, Optional, Dict
from pydantic import BaseModel

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

class CustomerSummary(BaseModel):
    id: int
    customer_code: str
    full_name: str
    email: str
    phone_masked: str
    account_number_masked: str
    kyc_status: str
    risk_tier: str

class AccessRequest(BaseModel):
    purpose: str
    ticket_id: Optional[str] = None
    justification: Optional[str] = None
    username: Optional[str] = "support_alice"

class TransactionDetail(BaseModel):
    id: int
    tx_code: str
    merchant: str
    category: str
    amount: str
    status: str
    timestamp: str

class AccessAuditMeta(BaseModel):
    purpose: str
    exposure_points_charged: int
    fields_disclosed: List[str]
    fields_masked: List[str]
    fields_redacted: List[str]

class CustomerDetailResponse(BaseModel):
    id: int
    customer_code: str
    full_name: str
    email: str
    phone: str
    account_number: str
    pan: str
    balance: str
    credit_score: Optional[int] = None
    kyc_status: str
    risk_tier: str
    transactions: List[TransactionDetail]
    access_meta: AccessAuditMeta

