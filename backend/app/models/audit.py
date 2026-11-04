from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AuditLog(Base):
    """
    Tamper-evident audit trail recording every access attempt,
    including the employee's role, declared business purpose, and fields disclosed.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    customer_id = Column(Integer, nullable=True)
    customer_code = Column(String(20), nullable=True)
    purpose = Column(String(100), nullable=False)
    ticket_id = Column(String(50), nullable=True)
    accessed_fields = Column(String(255), nullable=False)  # Comma-separated list of unmasked/accessed fields
    action_type = Column(String(50), nullable=False)       # VIEW_MASKED, UNMASK_FIELD, EXPORT, SEARCH
    exposure_points = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    status = Column(String(20), default="GRANTED")         # GRANTED, DENIED, THROTTLED


class SecurityIncident(Base):
    """
    High-priority security alerts generated when an employee exceeds exposure limits,
    attempts bulk data harvesting, or exhibits anomalous access velocity.
    """
    __tablename__ = "security_incidents"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    incident_type = Column(String(100), nullable=False)     # EXPOSURE_LIMIT_BREACH, BULK_EXFILTRATION_ATTEMPT, UNUSUAL_VELOCITY
    severity = Column(String(20), default="WARNING")        # INFO, WARNING, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    blocked = Column(Boolean, default=True)
    ip_address = Column(String(50), default="127.0.0.1")

