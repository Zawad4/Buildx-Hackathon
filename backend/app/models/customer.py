from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(20), unique=True, index=True, nullable=False)
    
    # Non-sensitive plain metadata for search & indexing
    full_name = Column(String(100), index=True, nullable=False)
    email = Column(String(100), index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    kyc_status = Column(String(20), default="VERIFIED")  # VERIFIED, PENDING
    risk_tier = Column(String(20), default="LOW")        # LOW, MEDIUM, HIGH
    credit_score = Column(Integer, default=750)
    
    # Sensitive Banking Fields - STORED STRICTLY AS AES-256-GCM CIPHERTEXT + UNIQUE NONCE
    account_number_enc = Column(String(255), nullable=False)
    account_number_nonce = Column(String(64), nullable=False)
    
    pan_enc = Column(String(255), nullable=False)
    pan_nonce = Column(String(64), nullable=False)
    
    balance_enc = Column(String(255), nullable=False)
    balance_nonce = Column(String(64), nullable=False)

    created_at = Column(DateTime, default=utc_now)
    
    # Relationship to banking transactions
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")

