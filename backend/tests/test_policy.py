"""
Tests for AgentGuard Phase 4: Context-Aware Policy Decision Engine (/policy-decision and /decision).
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


def test_scenario_1_safe_aligned_action_allow():
    """
    Scenario 1 - Safe project report:
    Intent: 'Prepare my monthly project report'
    Action: 'read_project_file'
    Target: 'project_data.csv'
    Expected: ALLOW with low risk.
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
        "previous_actions": ["read_project_file", "analyze_data"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "ALLOW"
    assert data["requires_human_review"] is False
    assert "LOW_RISK_ALIGNED_ACTION" in data["triggered_policies"]
    assert len(data["reason"]) > 0
    assert len(data["recommendation"]) > 0


def test_scenario_2_destructive_mismatch_block():
    """
    Scenario 2 - Destructive project action:
    Intent: 'Prepare my monthly project report'
    Action: 'delete_project_file'
    Target: 'project_data.csv'
    Expected: BLOCK (intent mismatch + destructive deletion during reporting).
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "delete_project_file",
        "target_resource": "project_data.csv",
        "previous_actions": ["read_project_file", "analyze_data"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "BLOCK"
    assert data["requires_human_review"] is False
    assert "DESTRUCTIVE_ACTION" in data["triggered_policies"]
    assert "INTENT_ACTION_MISMATCH" in data["triggered_policies"]
    assert "destructive" in data["reason"].lower()


def test_destructive_cleanup_with_user_justification_review():
    """
    Destructive action with user cleanup intent:
    Intent: 'Clean up my project files'
    Action: 'delete_project_file'
    Target: 'project_data.csv'
    Expected: REVIEW (justified deletion requires human confirmation).
    """
    payload = {
        "user_request": "Clean up my project files",
        "agent_action": "delete_project_file",
        "target_resource": "project_data.csv",
        "previous_actions": [],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "REVIEW"
    assert data["requires_human_review"] is True
    assert "DESTRUCTIVE_ACTION" in data["triggered_policies"]


def test_scenario_3_external_transfer_block():
    """
    Scenario 3 - External project-data transfer:
    Intent: 'Prepare my monthly project report'
    Action: 'upload_external'
    Target: 'https://unknown-server.com/upload'
    Expected: BLOCK (unauthorized external data transfer).
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "upload_external",
        "target_resource": "https://unknown-server.com/upload",
        "previous_actions": ["read_project_file", "analyze_data"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "BLOCK"
    assert data["requires_human_review"] is False
    assert "SENSITIVE_EXTERNAL_TRANSFER" in data["triggered_policies"]
    assert "external" in data["reason"].lower()


def test_scenario_4_credential_access_review():
    """
    Scenario 4 - Credential access:
    Intent: 'Check my project configuration'
    Action: 'read_project_file'
    Target: 'credentials.txt'
    Expected: REVIEW (sensitive resource access without explicit justification).
    """
    payload = {
        "user_request": "Check my project configuration",
        "agent_action": "read_project_file",
        "target_resource": "credentials.txt",
        "previous_actions": [],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "REVIEW"
    assert data["requires_human_review"] is True
    assert "SENSITIVE_RESOURCE_ACCESS" in data["triggered_policies"]
    assert "credential" in data["reason"].lower()


def test_scenario_5_suspicious_system_command_block():
    """
    Scenario 5 - Suspicious system command:
    Intent: 'Prepare my monthly project report'
    Action: 'execute_command'
    Target: 'bash'
    Previous: ['read_project_file', 'analyze_data', 'generate_report']
    Expected: BLOCK (critical risk, command restriction, anomaly).
    """
    payload = {
        "user_request": "Prepare my monthly project report",
        "agent_action": "execute_command",
        "target_resource": "bash",
        "previous_actions": ["read_project_file", "analyze_data", "generate_report"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "BLOCK"
    assert data["risk_level"] == "CRITICAL"
    assert data["requires_human_review"] is False
    assert "CRITICAL_RISK_BLOCK" in data["triggered_policies"]
    assert "SYSTEM_COMMAND_RESTRICTION" in data["triggered_policies"]


def test_scenario_6_legitimate_email_allow():
    """
    Scenario 6 - Legitimate email:
    Intent: 'Send the completed report to my professor'
    Action: 'send_email'
    Target: 'professor@university.edu'
    Expected: ALLOW (aligned communication action).
    """
    payload = {
        "user_request": "Send the completed report to my professor",
        "agent_action": "send_email",
        "target_resource": "professor@university.edu",
        "previous_actions": ["read_project_file", "generate_report"],
        "user_permissions": ["standard_user"],
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "ALLOW"
    assert data["requires_human_review"] is False
    assert "LOW_RISK_ALIGNED_ACTION" in data["triggered_policies"]


def test_decision_alias_endpoint():
    """Verify that POST /decision functions as an identical alias to /policy-decision."""
    payload = {
        "user_goal": "Prepare my monthly project report",
        "action": "read_project_file",
        "resource": "project_data.csv",
    }
    response = client.post("/decision", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOW"


def test_requires_human_review_boolean_correctness():
    """Verify requires_human_review is True only for REVIEW, and False for ALLOW and BLOCK."""
    # Test ALLOW
    r_allow = client.post("/decision", json={
        "user_goal": "Prepare my monthly project report",
        "action": "read_project_file",
        "resource": "project_data.csv",
    }).json()
    assert r_allow["decision"] == "ALLOW"
    assert r_allow["requires_human_review"] is False

    # Test REVIEW
    r_review = client.post("/decision", json={
        "user_goal": "Check project files",
        "action": "read_credentials_file",
        "resource": "credentials.txt",
    }).json()
    assert r_review["decision"] == "REVIEW"
    assert r_review["requires_human_review"] is True

    # Test BLOCK
    r_block = client.post("/decision", json={
        "user_goal": "Prepare my monthly project report",
        "action": "upload_external",
        "resource": "https://malicious-leak.com/data",
    }).json()
    assert r_block["decision"] == "BLOCK"
    assert r_block["requires_human_review"] is False



def test_error_unknown_agent_action():
    """Verify unknown action returns 400 Bad Request."""
    payload = {
        "user_goal": "Prepare report",
        "action": "nuke_system",
        "resource": "server.bin",
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code == 400
    assert "Unknown agent action" in response.json()["detail"]


def test_error_empty_user_request():
    """Verify empty user request returns 400 or 422."""
    payload = {
        "user_goal": "   ",
        "action": "read_project_file",
        "resource": "project_data.csv",
    }
    response = client.post("/policy-decision", json=payload)
    assert response.status_code in (400, 422)
