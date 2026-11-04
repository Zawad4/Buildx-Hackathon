from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel

class FieldAction(str, Enum):
    PLAIN = "PLAIN"           # Display non-sensitive data as is
    MASKED = "MASKED"         # Apply privacy mask (e.g. •••• •••• 1234)
    DECRYPTED = "DECRYPTED"   # Decrypt with AES-256-GCM and reveal plaintext
    REDACTED = "REDACTED"     # Completely withhold with placeholder

class PolicyDecision(BaseModel):
    is_allowed: bool
    denial_reason: Optional[str] = None
    purpose: str
    exposure_points: int
    field_actions: Dict[str, FieldAction]

class ABACPolicyEngine:
    """
    Context-Aware Attribute-Based Access Control (ABAC) Policy Engine.
    Evaluates:
      Access Granted = f(Employee Role, Declared Purpose, Resource Fields, Context/Ticket)
    """

    # Validated business purposes
    PURPOSES = {
        "GENERAL_INQUIRY": {
            "name": "General Inquiry",
            "description": "Basic verification of customer identity and contact info.",
            "allowed_roles": {"SUPPORT", "LOAN_OFFICER", "COMPLIANCE_AUDITOR", "ADMIN"},
            "exposure_points": 1,
            "fields": {
                "full_name": FieldAction.PLAIN,
                "email": FieldAction.PLAIN,
                "phone": FieldAction.MASKED,
                "account_number": FieldAction.MASKED,
                "pan": FieldAction.REDACTED,
                "balance": FieldAction.REDACTED,
                "credit_score": FieldAction.REDACTED,
                "transactions": FieldAction.REDACTED,
            }
        },
        "DISPUTE_RESOLUTION": {
            "name": "Dispute Resolution",
            "description": "Investigate failed or contested payments and account charges.",
            "allowed_roles": {"SUPPORT", "COMPLIANCE_AUDITOR", "ADMIN"},
            "exposure_points": 4,
            "fields": {
                "full_name": FieldAction.PLAIN,
                "email": FieldAction.PLAIN,
                "phone": FieldAction.PLAIN,
                "account_number": FieldAction.MASKED,
                "pan": FieldAction.REDACTED,
                "balance": FieldAction.DECRYPTED,
                "credit_score": FieldAction.REDACTED,
                "transactions": FieldAction.DECRYPTED,
            }
        },
        "LOAN_UNDERWRITING": {
            "name": "Loan Underwriting",
            "description": "Assess credit eligibility, tax verification, and debt capacity.",
            "allowed_roles": {"LOAN_OFFICER", "COMPLIANCE_AUDITOR", "ADMIN"},
            "exposure_points": 6,
            "fields": {
                "full_name": FieldAction.PLAIN,
                "email": FieldAction.PLAIN,
                "phone": FieldAction.PLAIN,
                "account_number": FieldAction.MASKED,
                "pan": FieldAction.DECRYPTED,       # Tax ID required for underwriting
                "balance": FieldAction.DECRYPTED,   # Capacity evaluation
                "credit_score": FieldAction.PLAIN,
                "transactions": FieldAction.REDACTED,
            }
        },
        "FRAUD_INVESTIGATION": {
            "name": "Fraud Investigation",
            "description": "Deep-dive inquiry into flagged anomalous activity or stolen credentials.",
            "allowed_roles": {"SUPPORT", "COMPLIANCE_AUDITOR", "ADMIN"},
            "exposure_points": 10,
            "fields": {
                "full_name": FieldAction.PLAIN,
                "email": FieldAction.PLAIN,
                "phone": FieldAction.PLAIN,
                "account_number": FieldAction.DECRYPTED,
                "pan": FieldAction.DECRYPTED,
                "balance": FieldAction.DECRYPTED,
                "credit_score": FieldAction.PLAIN,
                "transactions": FieldAction.DECRYPTED,
            }
        },
        "COMPLIANCE_AUDIT": {
            "name": "Compliance Audit",
            "description": "Statutory regulatory inspection and audit sampling.",
            "allowed_roles": {"COMPLIANCE_AUDITOR", "ADMIN"},
            "exposure_points": 8,
            "fields": {
                "full_name": FieldAction.PLAIN,
                "email": FieldAction.PLAIN,
                "phone": FieldAction.PLAIN,
                "account_number": FieldAction.DECRYPTED,
                "pan": FieldAction.DECRYPTED,
                "balance": FieldAction.DECRYPTED,
                "credit_score": FieldAction.PLAIN,
                "transactions": FieldAction.DECRYPTED,
            }
        }
    }

    @classmethod
    def evaluate(cls, user_role: str, purpose_key: str, ticket_id: Optional[str] = None) -> PolicyDecision:
        """
        Evaluates the ABAC access request.
        
        Args:
            user_role: The role of the authenticated employee.
            purpose_key: The declared business purpose (e.g. 'DISPUTE_RESOLUTION').
            ticket_id: Optional helpdesk or loan application ticket identifier.
        """
        normalized_purpose = purpose_key.strip().upper()
        
        if normalized_purpose not in cls.PURPOSES:
            return PolicyDecision(
                is_allowed=False,
                denial_reason=f"Invalid or unrecognized purpose: '{purpose_key}'.",
                purpose=normalized_purpose,
                exposure_points=0,
                field_actions={}
            )
            
        policy = cls.PURPOSES[normalized_purpose]
        
        # Check role authorization for this specific purpose
        if user_role not in policy["allowed_roles"]:
            return PolicyDecision(
                is_allowed=False,
                denial_reason=(
                    f"Access Denied: Role '{user_role}' is not authorized to request data "
                    f"for business purpose '{policy['name']}'."
                ),
                purpose=normalized_purpose,
                exposure_points=0,
                field_actions={}
            )

        # Dispute or Fraud purposes benefit from tracking a ticket reference
        actions = dict(policy["fields"])
        
        return PolicyDecision(
            is_allowed=True,
            denial_reason=None,
            purpose=normalized_purpose,
            exposure_points=policy["exposure_points"],
            field_actions=actions
        )

    @classmethod
    def list_available_purposes(cls, user_role: str) -> List[dict]:
        """Lists all purposes available to the given role."""
        return [
            {
                "id": k,
                "name": v["name"],
                "description": v["description"],
                "exposure_points": v["exposure_points"]
            }
            for k, v in cls.PURPOSES.items()
            if user_role in v["allowed_roles"]
        ]

