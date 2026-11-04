import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)

def get_auth_token(username: str = "support_alice", password: str = "Password123!") -> str:
    """Helper to authenticate and return a JWT access token."""
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]

def test_exposure_status_initial():
    """Verify exposure status endpoint reports initial budget cleanly."""
    token = get_auth_token("support_alice")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/audit/exposure/status", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "support_alice"
    assert "points_used" in data
    assert data["max_budget"] == 50

def test_cumulative_exposure_and_lockout():
    """
    Simulates employee data harvesting:
    Repeatedly accesses records until the 50-point budget is breached.
    Verifies automatic lockout and security incident generation.
    """
    token = get_auth_token("support_alice")
    headers = {"Authorization": f"Bearer {token}"}

    # Dispute resolution costs 4 points.
    # 13 requests = 52 points, which breaches the 50-point limit!
    locked = False
    for i in range(1, 15):
        cust_id = (i % 20) + 1
        resp = client.post(
            f"/api/v1/customers/{cust_id}/access",
            headers=headers,
            json={"purpose": "DISPUTE_RESOLUTION", "ticket_id": f"TICK-{i}"}
        )
        if resp.status_code == 403 and "budget exceeded" in resp.json()["detail"].lower():
            locked = True
            break

    assert locked, "Expected session to be locked after exceeding exposure budget!"

    # Verify that status now reports is_locked = True
    status_resp = client.get("/api/v1/audit/exposure/status", headers=headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["is_locked"] is True
    assert "limit exceeded" in status_data["lock_reason"].lower()

def test_bulk_export_blocking():
    """
    Verifies that an attempt to export >10 records triggers exfiltration prevention.
    """
    token = get_auth_token("loan_bob")
    headers = {"Authorization": f"Bearer {token}"}

    # Attempt to export 15 customer IDs
    export_req = {
        "customer_ids": list(range(1, 16)),
        "format": "CSV",
        "purpose": "GENERAL_INQUIRY"
    }

    resp = client.post("/api/v1/customers/export", headers=headers, json=export_req)
    assert resp.status_code == 403
    assert "exfiltration" in resp.json()["detail"].lower()

def test_admin_unlock_and_incident_review():
    """
    Verifies that Admin David can inspect security incidents and unlock an employee's session.
    """
    admin_token = get_auth_token("admin_david")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Admin inspects incident feed
    incidents_resp = client.get("/api/v1/audit/incidents", headers=admin_headers)
    assert incidents_resp.status_code == 200
    incidents = incidents_resp.json()
    assert len(incidents) > 0
    
    incident_types = [inc["incident_type"] for inc in incidents]
    assert "EXPOSURE_LIMIT_BREACH" in incident_types or "BULK_EXFILTRATION_ATTEMPT" in incident_types

    # 2. Admin resets Alice's session (Alice user_id = 1) and Bob's session (Bob user_id = 2)
    reset_resp = client.post("/api/v1/audit/exposure/reset/1", headers=admin_headers)
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "success"

    reset_bob_resp = client.post("/api/v1/audit/exposure/reset/2", headers=admin_headers)
    assert reset_bob_resp.status_code == 200

    # 3. Verify Alice is now unlocked
    alice_token = get_auth_token("support_alice")
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    alice_status = client.get("/api/v1/audit/exposure/status", headers=alice_headers).json()
    assert alice_status["is_locked"] is False
    assert alice_status["points_used"] == 0

