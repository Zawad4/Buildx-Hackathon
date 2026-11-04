from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.exposure import SessionExposure
from app.models.audit import AuditLog, SecurityIncident
from app.models.user import User

class ExposureEngine:
    """
    Intelligent Exposure Budget and Leakage Prevention Engine.
    Tracks session-level exposure, enforces quotas, and detects data harvesting.
    """

    @classmethod
    def get_or_create_session(cls, db: Session, user: User) -> SessionExposure:
        """Retrieves or creates an active session exposure tracker for the user."""
        session_tracker = db.query(SessionExposure).filter(
            SessionExposure.user_id == user.id
        ).order_by(SessionExposure.last_accessed_at.desc()).first()

        if not session_tracker:
            session_tracker = SessionExposure(
                user_id=user.id,
                session_token=f"sess-{user.id}-{int(datetime.now(timezone.utc).timestamp())}",
                points_used=0,
                max_budget=settings.DEFAULT_SESSION_EXPOSURE_BUDGET,
                records_accessed_count=0,
                is_locked=False,
                created_at=datetime.now(timezone.utc),
                last_accessed_at=datetime.now(timezone.utc)
            )
            db.add(session_tracker)
            db.commit()
            db.refresh(session_tracker)

        return session_tracker

    @classmethod
    def check_and_charge_exposure(
        cls,
        db: Session,
        user: User,
        points: int,
        customer_code: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates whether user has enough remaining exposure budget.
        If budget is exceeded, locks the session and creates a Security Incident.
        
        Returns:
            Tuple[is_allowed: bool, rejection_message: Optional[str]]
        """
        session_tracker = cls.get_or_create_session(db, user)

        # 1. Check if session is already locked
        if session_tracker.is_locked:
            return False, f"Access blocked: Session is locked. Reason: {session_tracker.lock_reason}"

        # 2. Check if this request breaches the cumulative exposure budget
        projected_points = session_tracker.points_used + points
        if projected_points > session_tracker.max_budget:
            # Lock the session immediately
            session_tracker.is_locked = True
            session_tracker.lock_reason = (
                f"Session exposure limit exceeded. Attempted {projected_points}/{session_tracker.max_budget} points."
            )
            session_tracker.last_accessed_at = datetime.now(timezone.utc)

            # Generate High-Severity Security Incident
            incident = SecurityIncident(
                user_id=user.id,
                username=user.username,
                incident_type="EXPOSURE_LIMIT_BREACH",
                severity="HIGH",
                description=(
                    f"Employee '{user.username}' ({user.role}) breached session exposure limit "
                    f"({projected_points}/{session_tracker.max_budget} points) while requesting record '{customer_code}'."
                ),
                blocked=True,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(incident)
            db.commit()

            return False, (
                f"Access Denied by Adaptive Vault X: Cumulative exposure budget exceeded "
                f"({projected_points}/{session_tracker.max_budget} points). Session has been locked for review."
            )

        # 3. Request approved: deduct points and update session
        session_tracker.points_used = projected_points
        session_tracker.records_accessed_count += 1
        session_tracker.last_accessed_at = datetime.now(timezone.utc)
        db.commit()

        # 4. Check for anomalous access velocity (e.g. >5 records in past 60s)
        cls._check_velocity(db, user)

        return True, None

    @classmethod
    def _check_velocity(cls, db: Session, user: User):
        """Detects high-frequency record browsing (potential automated scraping)."""
        sixty_seconds_ago = datetime.now(timezone.utc) - timedelta(seconds=60)
        recent_count = db.query(AuditLog).filter(
            AuditLog.user_id == user.id,
            AuditLog.timestamp >= sixty_seconds_ago
        ).count()

        if recent_count >= 5:
            # Log an incident alert for compliance review
            incident = SecurityIncident(
                user_id=user.id,
                username=user.username,
                incident_type="ANOMALOUS_ACCESS_VELOCITY",
                severity="WARNING",
                description=(
                    f"Anomalous access velocity detected for '{user.username}'. "
                    f"Accessed {recent_count} records in under 60 seconds."
                ),
                blocked=False,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(incident)
            db.commit()

    @classmethod
    def evaluate_bulk_export(
        cls,
        db: Session,
        user: User,
        record_count: int,
        purpose: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Guards against bulk data harvesting.
        Blocks requests attempting to export more than 10 records without supervisor/admin rights.
        """
        MAX_SAFE_EXPORT_THRESHOLD = 10

        if record_count > MAX_SAFE_EXPORT_THRESHOLD and user.role not in {"ADMIN", "COMPLIANCE_AUDITOR"}:
            # Trigger Critical Exfiltration Incident
            incident = SecurityIncident(
                user_id=user.id,
                username=user.username,
                incident_type="BULK_EXFILTRATION_ATTEMPT",
                severity="CRITICAL",
                description=(
                    f"CRITICAL: User '{user.username}' ({user.role}) attempted unauthorized bulk export of "
                    f"{record_count} sensitive customer records under purpose '{purpose}'."
                ),
                blocked=True,
                timestamp=datetime.now(timezone.utc)
            )
            db.add(incident)

            # Lock session
            session_tracker = cls.get_or_create_session(db, user)
            session_tracker.is_locked = True
            session_tracker.lock_reason = "Unauthorized bulk data export attempt."
            db.commit()

            return False, (
                f"Export Blocked: Unauthorized bulk exfiltration attempt ({record_count} records). "
                f"Incident logged and session locked."
            )

        return True, None

    @classmethod
    def reset_user_session(cls, db: Session, target_user_id: int) -> bool:
        """Allows an administrator to unlock and reset an employee's session exposure budget."""
        session_tracker = db.query(SessionExposure).filter(
            SessionExposure.user_id == target_user_id
        ).first()

        if session_tracker:
            session_tracker.points_used = 0
            session_tracker.is_locked = False
            session_tracker.lock_reason = None
            session_tracker.last_accessed_at = datetime.now(timezone.utc)
            db.commit()
            return True
        return False

