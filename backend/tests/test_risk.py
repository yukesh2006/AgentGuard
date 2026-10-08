"""
Tests for AgentGuard Phase 3: Behavioral Anomaly Detection & Risk Assessment Engine.
"""

import sys
from pathlib import Path

# Ensure project root and backend dir are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_scenario_1_normal():
    """
    SCENARIO 1 - NORMAL:
    User: 'Prepare my monthly project report'
    Previous: ['read_project_file', 'analyze_data']
    Current: 'read_project_file'
    Target: 'project_data.csv'
    Expected: Relatively low risk, no major anomaly, reasonable consistency.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
        "previous_actions": ["read_project_file", "analyze_data"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_level"] in ("LOW", "MEDIUM")
    assert data["risk_score"] < 40.0
    assert data["behavior"]["is_anomaly"] is False
    assert data["behavior"]["severity"] == "low"
    assert isinstance(data["factors"], list)


def test_scenario_2_destructive():
    """
    SCENARIO 2 - DESTRUCTIVE:
    User: 'Prepare my monthly project report'
    Previous: ['read_project_file', 'analyze_data']
    Current: 'delete_project_file'
    Target: 'project_data.csv'
    Expected: Increased risk, destructive factor present, not necessarily CRITICAL.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "delete_project_file",
        "target_resource": "project_data.csv",
        "previous_actions": ["read_project_file", "analyze_data"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_score"] > 25.0
    assert data["risk_level"] in ("MEDIUM", "HIGH")

    # Verify destructive factor is present with positive impact
    factor_names = [f["factor"] for f in data["factors"]]
    assert "destructive_action" in factor_names
    destructive_factor = next(f for f in data["factors"] if f["factor"] == "destructive_action")
    assert destructive_factor["impact"] > 0


def test_scenario_3_external_transfer():
    """
    SCENARIO 3 - EXTERNAL TRANSFER:
    User: 'Prepare my monthly project report'
    Previous: ['read_project_file', 'analyze_data']
    Current: 'upload_external'
    Target: 'https://unknown-server.com/upload'
    Expected: High-risk contribution from external transfer, lower intent consistency, elevated risk.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "upload_external",
        "target_resource": "https://unknown-server.com/upload",
        "previous_actions": ["read_project_file", "analyze_data"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_score"] >= 50.0
    assert data["risk_level"] in ("HIGH", "CRITICAL")

    factor_names = [f["factor"] for f in data["factors"]]
    assert "external_data_transfer" in factor_names
    ext_factor = next(f for f in data["factors"] if f["factor"] == "external_data_transfer")
    assert ext_factor["impact"] > 0


def test_scenario_4_sensitive_resource():
    """
    SCENARIO 4 - SENSITIVE RESOURCE:
    User: 'Prepare my monthly project report'
    Current: 'read_project_file'
    Target: 'credentials.txt'
    Expected: Sensitive resource factor, increased risk.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
        "target_resource": "credentials.txt",
        "previous_actions": [],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_score"] >= 25.0
    factor_names = [f["factor"] for f in data["factors"]]
    assert "resource_sensitivity" in factor_names
    sens_factor = next(f for f in data["factors"] if f["factor"] == "resource_sensitivity")
    assert sens_factor["impact"] > 0


def test_scenario_5_behavioral_escalation():
    """
    SCENARIO 5 - BEHAVIORAL ESCALATION:
    Previous: ['read_project_file', 'analyze_data', 'generate_report']
    Current: 'execute_command'
    Target: 'bash'
    Expected: Behavioral anomaly signal or elevated behavioral risk, system-command risk factor.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "execute_command",
        "target_resource": "bash",
        "previous_actions": ["read_project_file", "analyze_data", "generate_report"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Elevated risk with system command and escalation
    assert data["risk_score"] >= 50.0
    assert data["risk_level"] in ("HIGH", "CRITICAL")

    factor_names = [f["factor"] for f in data["factors"]]
    assert "system_command_execution" in factor_names


def test_scenario_6_normal_communication():
    """
    SCENARIO 6 - NORMAL COMMUNICATION:
    User: 'Send the completed report to my professor'
    Previous: ['read_project_file', 'generate_report']
    Current: 'send_email'
    Target: 'professor@university.edu'
    Expected: Relatively low risk, communication action aligned with intent.
    """
    payload = {
        "user_request": "Send the completed report to my professor",
        "agent_action": "send_email",
        "target_resource": "professor@university.edu",
        "previous_actions": ["read_project_file", "generate_report"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["risk_level"] in ("LOW", "MEDIUM")
    assert data["risk_score"] < 40.0


def test_missing_previous_actions_defaults_gracefully():
    """Verify that requests without previous_actions default gracefully."""
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "risk_score" in data
    assert "risk_level" in data


def test_error_unknown_action():
    """Verify that an unknown action returns HTTP 400."""
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "exploit_vulnerability",
        "target_resource": "system.bin",
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code == 400
    assert "Unknown agent action" in response.json()["detail"]


def test_error_empty_user_request():
    """Verify that an empty user request returns HTTP 400 or 422."""
    payload = {
        "user_request": "   ",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code in (400, 422)


def test_error_missing_target_resource():
    """Verify that missing target_resource returns HTTP 400 or 422."""
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
    }
    response = client.post("/risk-assessment", json=payload)
    assert response.status_code in (400, 422)
