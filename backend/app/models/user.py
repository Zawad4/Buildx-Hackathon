from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # SUPPORT, LOAN_OFFICER, COMPLIANCE_AUDITOR, ADMIN
    department = Column(String(50), nullable=False)  # Customer Ops, Lending, Compliance, IT Security
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

