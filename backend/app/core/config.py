import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = (BASE_DIR / "vault.db").resolve()

class Settings(BaseModel):
    PROJECT_NAME: str = "ADAPTIVE VAULT X"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "adaptive-vault-x-insecure-dev-secret-key-32bytes!")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Database Configuration (Fixed absolute path for SQLite to prevent working-directory mismatches)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE.as_posix()}")
    
    # AES-256-GCM Master Key (32 bytes / 256 bits hex-encoded)
    VAULT_MASTER_KEY_HEX: str = os.getenv(
        "VAULT_MASTER_KEY_HEX",
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )
    
    # Adaptive Exposure Default Budget (points per session)
    DEFAULT_SESSION_EXPOSURE_BUDGET: int = 50

settings = Settings()
