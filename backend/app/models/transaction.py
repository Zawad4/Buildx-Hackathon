from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    tx_code = Column(String(30), unique=True, index=True, nullable=False)
    merchant = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # GROCERY, TRAVEL, UTILITY, TRANSFER
    
    # Sensitive monetary amount encrypted with AES-256-GCM
    amount_enc = Column(String(255), nullable=False)
    amount_nonce = Column(String(64), nullable=False)
    
    status = Column(String(20), default="SUCCESS")  # SUCCESS, FAILED, DISPUTED
    timestamp = Column(DateTime, default=utc_now)

    customer = relationship("Customer", back_populates="transactions")

