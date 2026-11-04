import re
from typing import Any

class DataMasker:
    """
    Dynamic Data Masking and Redaction Engine.
    Enforces privacy-preserving data utility for non-privileged views.
    """

    @staticmethod
    def mask_account_number(account_no: str) -> str:
        """Keeps only last 4 digits visible: '•••• •••• 1234'"""
        clean = re.sub(r"\s+", "", str(account_no))
        if len(clean) <= 4:
            return "••••"
        return "•••• •••• " + clean[-4:]

    @staticmethod
    def mask_pan(pan: str) -> str:
        """Indian PAN format (e.g. ABCDE1234F) -> '••••••234F' (masks first 6 chars, retains 10-char length)"""
        clean = str(pan).strip().upper()
        if len(clean) != 10:
            return "••••••••••"
        return "••••••" + clean[-4:]

    @staticmethod
    def mask_balance(balance_val: Any) -> str:
        """Conceals monetary balance: '₹ ••,•••.••'"""
        return "₹ ••,•••.••"

    @staticmethod
    def mask_email(email: str) -> str:
        """Masks email: 'rahul.sharma@bank.com' -> 'r••••a@bank.com'"""
        if not email or "@" not in email:
            return "••••@••••.com"
        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = local[0] + "•"
        else:
            masked_local = local[0] + "•" * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Masks phone number: '+91 9876543210' -> '+91 ••••• •3210'"""
        digits = re.sub(r"\D", "", str(phone))
        if len(digits) < 4:
            return "••••••••••"
        return f"+91 ••••• •{digits[-4:]}"

    @staticmethod
    def redact(field_name: str) -> str:
        """Standard placeholder for completely restricted fields."""
        return f"[REDACTED: Requires '{field_name}' authorization]"

    @classmethod
    def mask_by_field(cls, field_name: str, value: Any) -> str:
        """Applies appropriate masking strategy based on the field identity."""
        if value is None:
            return ""
        str_val = str(value)
        if field_name in ("account_number", "account_no"):
            return cls.mask_account_number(str_val)
        elif field_name in ("pan", "pan_card", "tax_id"):
            return cls.mask_pan(str_val)
        elif field_name in ("balance", "current_balance", "amount"):
            return cls.mask_balance(str_val)
        elif field_name == "email":
            return cls.mask_email(str_val)
        elif field_name in ("phone", "mobile"):
            return cls.mask_phone(str_val)
        else:
            return "••••••••"
