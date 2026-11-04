from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.core.database import Base
from app.core.config import settings

def utc_now():
    return datetime.now(timezone.utc)

class SessionExposure(Base):
    """
    Tracks cumulative sensitive data exposure per employee session.
    Protects against 'low-and-slow' insider data harvesting.
    """
    __tablename__ = "session_exposure"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_token = Column(String(100), index=True, nullable=False)
    
    # Cumulative exposure points accumulated during the session
    points_used = Column(Integer, default=0)
    max_budget = Column(Integer, default=settings.DEFAULT_SESSION_EXPOSURE_BUDGET)
    
    records_accessed_count = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    lock_reason = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    last_accessed_at = Column(DateTime, default=utc_now)

