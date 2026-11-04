import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)

def test_login_success():
    """Verify that employee Alice can log in with valid credentials and receive a JWT."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "support_alice", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "SUPPORT"
    assert data["user"]["username"] == "support_alice"

def test_login_invalid_password():
    """Verify that login fails with incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "support_alice", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_me_endpoint_requires_auth():
    """Verify that /me endpoint rejects unauthenticated requests."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_customer_search_masked_by_default():
    """Verify that customer search returns masked account numbers and phones."""
    # Login as Alice
    # Ensure clean session for test isolation
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.security.exposure_engine import ExposureEngine
    db = SessionLocal()
    alice = db.query(User).filter(User.username == "support_alice").first()
    if alice:
        ExposureEngine.reset_user_session(db, alice.id)
    db.close()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "support_alice", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Search for customer
    response = client.get("/api/v1/customers?q=Rahul", headers=headers)
    assert response.status_code == 200
    customers = response.json()
    assert len(customers) > 0
    cust = customers[0]
    assert "•••• •••• " in cust["account_number_masked"]
    assert "•" in cust["phone_masked"]

def test_abac_support_dispute_resolution():
    """
    Scenario: Alice (SUPPORT) needs to resolve a transaction dispute.
    ABAC Policy should:
      - Decrypt Balance
      - Decrypt Transactions
      - Mask Account Number
      - Redact PAN Card
    """
    # Ensure clean session for test isolation
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.security.exposure_engine import ExposureEngine
    db = SessionLocal()
    alice = db.query(User).filter(User.username == "support_alice").first()
    if alice:
        ExposureEngine.reset_user_session(db, alice.id)
    db.close()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "support_alice", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Access customer 1 with DISPUTE_RESOLUTION
    response = client.post(
        "/api/v1/customers/1/access",
        headers=headers,
        json={"purpose": "DISPUTE_RESOLUTION", "ticket_id": "TICKET-4481"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify field disclosure policies
    assert "₹" in data["balance"]
    assert len(data["transactions"]) > 0
    assert "•••• •••• " in data["account_number"]
    assert "[REDACTED" in data["pan"]
    assert data["credit_score"] is None
    assert data["access_meta"]["purpose"] == "DISPUTE_RESOLUTION"

def test_abac_support_denied_loan_underwriting():
    """
    Scenario: Alice (SUPPORT) tries to invoke LOAN_UNDERWRITING.
    ABAC Policy should reject with 403 Forbidden!
    """
    # Ensure clean session for test isolation
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.security.exposure_engine import ExposureEngine
    db = SessionLocal()
    alice = db.query(User).filter(User.username == "support_alice").first()
    if alice:
        ExposureEngine.reset_user_session(db, alice.id)
    db.close()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "support_alice", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt forbidden purpose
    response = client.post(
        "/api/v1/customers/1/access",
        headers=headers,
        json={"purpose": "LOAN_UNDERWRITING"}
    )
    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()

def test_abac_loan_officer_allowed_loan_underwriting():
    """
    Scenario: Bob (LOAN_OFFICER) needs to underwrite a loan.
    ABAC Policy should:
      - Decrypt PAN (for tax & identity check)
      - Decrypt Balance (for capacity)
      - Show Credit Score
      - Redact Transactions
    """
    # Ensure clean session for test isolation
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.security.exposure_engine import ExposureEngine
    db = SessionLocal()
    bob = db.query(User).filter(User.username == "loan_bob").first()
    if bob:
        ExposureEngine.reset_user_session(db, bob.id)
    db.close()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "loan_bob", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Bob accesses customer 1 with LOAN_UNDERWRITING
    response = client.post(
        "/api/v1/customers/1/access",
        headers=headers,
        json={"purpose": "LOAN_UNDERWRITING", "ticket_id": "LOAN-APP-990"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # PAN is unmasked for loan officer
    assert not data["pan"].startswith("[REDACTED")
    assert not "•" in data["pan"]
    assert "₹" in data["balance"]
    assert data["credit_score"] is not None
    assert len(data["transactions"]) == 0  # Redacted

