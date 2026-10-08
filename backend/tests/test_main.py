"""
Tests for AgentGuard Phase 1 Foundation Endpoints.
"""

import sys
from pathlib import Path

# Ensure the backend directory is in the Python search path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    """Verify that GET / returns the correct service running info."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "AgentGuard",
        "message": "Context-Aware AI Intent Firewall",
        "status": "running",
    }


def test_health_check():
    """Verify that GET /health returns the exact expected health status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "AgentGuard",
    }


if __name__ == "__main__":
    print("Running basic endpoint tests...")
    test_read_root()
    print("[PASS] GET / passed")
    test_health_check()
    print("[PASS] GET /health passed")
    print("All Phase 1 tests passed successfully!")

