import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["security_layer"] == "Active"

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ADAPTIVE VAULT X" in response.json()["message"]

