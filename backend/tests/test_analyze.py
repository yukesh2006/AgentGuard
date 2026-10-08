"""
Tests for AgentGuard Phase 2: Intent and Context Intelligence (/analyze endpoint).
"""

import sys
from pathlib import Path

# Ensure the backend directory is in the Python search path
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_scenario_1_consistent_action():
    """
    TEST 1 - CONSISTENT:
    User: 'Prepare my monthly project report'
    Action: 'read_project_file'
    Target: 'project_data.csv'
    Expected: High or reasonable semantic compatibility.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Intent verification
    assert "report" in data["intent"]["goal"].lower() or "report" in data["intent"]["intent"].lower()
    assert data["intent"]["confidence"] > 0.0

    # Context & Action verification
    assert data["context"]["resource"] == "project_data.csv"
    assert data["context"]["resource_type"] == "file"
    assert data["action"]["name"] == "read_project_file"

    # Compatibility: reasonable or high
    assert data["consistency"]["compatibility"] in ("high", "medium")
    assert isinstance(data["consistency"]["similarity_score"], float)

    # Signals
    signal_types = [s["type"] for s in data["signals"]]
    assert "intent_action_consistency" in signal_types


def test_scenario_2_suspicious_action():
    """
    TEST 2 - SUSPICIOUS:
    User: 'Prepare my monthly project report'
    Action: 'delete_project_file'
    Target: 'project_data.csv'
    Expected: Lower compatibility than read action, and a negative contextual signal.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "delete_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Action & Context verification
    assert data["action"]["name"] == "delete_project_file"

    # Negative contextual signal for unexpected destructive action
    signal_types = [s["type"] for s in data["signals"]]
    assert "destructive_action_anomaly" in signal_types

    # Find the destructive signal and ensure severity is high
    destructive_signal = next(s for s in data["signals"] if s["type"] == "destructive_action_anomaly")
    assert destructive_signal["severity"] == "high"


def test_scenario_3_external_data_transfer():
    """
    TEST 3 - EXTERNAL DATA TRANSFER:
    User: 'Prepare my monthly project report'
    Action: 'upload_external'
    Target: 'https://unknown-server.com/upload'
    Expected: Negative contextual signal for unauthorized external transfer.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "upload_external",
        "target_resource": "https://unknown-server.com/upload",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["context"]["resource_type"] == "network_endpoint"
    assert data["consistency"]["compatibility"] in ("low", "medium")

    # Negative contextual signal for external data transfer
    signal_types = [s["type"] for s in data["signals"]]
    assert "external_data_transfer" in signal_types

    transfer_signal = next(s for s in data["signals"] if s["type"] == "external_data_transfer")
    assert transfer_signal["severity"] == "high"


def test_scenario_4_email_dispatch():
    """
    TEST 4 - EMAIL DISPATCH:
    User: 'Send the completed report to my professor'
    Action: 'send_email'
    Target: 'professor@university.edu'
    Expected: Reasonable compatibility and aligned communication signal.
    """
    payload = {
        "user_request": "Send the completed report to my professor",
        "agent_action": "send_email",
        "target_resource": "professor@university.edu",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["context"]["resource_type"] == "email_recipient"
    assert data["consistency"]["compatibility"] in ("high", "medium")

    signal_types = [s["type"] for s in data["signals"]]
    assert "communication_dispatch_aligned" in signal_types


def test_error_empty_user_request():
    """Verify that an empty user_request is rejected with a clear error."""
    payload = {
        "user_request": "   ",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code in (400, 422)


def test_error_missing_agent_action():
    """Verify that a missing agent_action is rejected with a clear error."""
    payload = {
        "user_request": "Prepare my monthly project report",
        "target_resource": "project_data.csv",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code in (400, 422)


def test_error_unknown_agent_action():
    """Verify that an unknown agent action is rejected with a clear error."""
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "hack_mainframe_now",
        "target_resource": "core.sys",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Unknown agent action" in data["detail"]


def test_error_missing_target_resource():
    """Verify that a missing target_resource is rejected with a clear error."""
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code in (400, 422)
