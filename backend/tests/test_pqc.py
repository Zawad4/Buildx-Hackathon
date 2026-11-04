import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)

def test_ml_kem_768_handshake():
    """Verify that the experimental ML-KEM-768 quantum-safe handshake runs and succeeds."""
    response = client.post("/api/v1/crypto/pqc-handshake")
    assert response.status_code == 200
    data = response.json()
    assert data["handshake_verified"] is True
    assert data["metrics"]["public_key_bytes"] == 1184
    assert data["metrics"]["ciphertext_bytes"] == 1088
    assert data["metrics"]["shared_secret_bits"] == 256
    assert data["metrics"]["total_handshake_ms"] >= 0
    assert "FIPS 203" in data["algorithm"]

