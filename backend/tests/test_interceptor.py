"""
Tests for AgentGuard Phase 5: Agent Interception & Safe Action Simulation (/intercept and /agent/intercept).
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root and backend dir are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.services.simulator import SafeActionSimulator
from app.models.interception import SimulationStatusEnum, ReviewStatusEnum

client = TestClient(app)


def test_scenario_1_safe_action_simulated_success():
    """
    Demo Scenario 1: Safe Action
    User Goal: Prepare my monthly project report.
    Agent Action: read_project_file
    Target: project_data.csv
    Expected: ALLOW + SIMULATED_SUCCESS, execution_permitted: True
    """
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "ALLOW"
    assert data["simulation_status"] == "SIMULATED_SUCCESS"
    assert data["execution_permitted"] is True
    assert data["requires_human_review"] is False
    assert data["action"] == "read_project_file"
    assert data["target_resource"] == "project_data.csv"
    assert data["interception_id"].startswith("AG-2026-")
    assert "LOW_RISK_ALIGNED_ACTION" in data["triggered_policies"]
    assert data["simulation_output"] is not None
    assert data["simulation_output"]["operation"] == "read_project_file"


def test_scenario_2_destructive_mismatch_blocked():
    """
    Demo Scenario 2: Destructive Action Mismatch
    User Goal: Prepare my monthly project report.
    Agent Action: delete_project_file
    Target: project_data.csv
    Expected: BLOCK + NOT_EXECUTED, execution_permitted: False
    """
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "delete_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "BLOCK"
    assert data["simulation_status"] == "NOT_EXECUTED"
    assert data["execution_permitted"] is False
    assert data["requires_human_review"] is False
    assert "DESTRUCTIVE_ACTION" in data["triggered_policies"]
    assert "INTENT_ACTION_MISMATCH" in data["triggered_policies"]
    assert data["simulation_output"] is None
    assert "blocked" in data["message"].lower()


def test_scenario_3_external_transfer_blocked():
    """
    Demo Scenario 3: External Transfer
    User Goal: Prepare my monthly project report.
    Agent Action: upload_external
    Target: unknown_external_server
    Expected: BLOCK + NOT_EXECUTED, execution_permitted: False
    """
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "upload_external",
        "target_resource": "unknown_external_server",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "BLOCK"
    assert data["simulation_status"] == "NOT_EXECUTED"
    assert data["execution_permitted"] is False
    assert data["requires_human_review"] is False
    assert "SENSITIVE_EXTERNAL_TRANSFER" in data["triggered_policies"]
    assert data["simulation_output"] is None


def test_scenario_4_sensitive_resource_waiting_for_review():
    """
    Demo Scenario 4: Sensitive Resource Access
    User Goal: Check my project configuration.
    Agent Action: read_project_file
    Target: credentials.txt
    Expected: REVIEW + WAITING_FOR_REVIEW, execution_permitted: False
    """
    payload = {
        "user_goal": "Check my project configuration.",
        "agent_action": "read_project_file",
        "target_resource": "credentials.txt",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "REVIEW"
    assert data["simulation_status"] == "WAITING_FOR_REVIEW"
    assert data["execution_permitted"] is False
    assert data["requires_human_review"] is True
    assert data["review_status"] == "PENDING"
    assert "SENSITIVE_RESOURCE_ACCESS" in data["triggered_policies"]
    assert data["simulation_output"] is None
    assert "approval" in data["message"].lower()


def test_scenario_5_system_command_blocked():
    """
    Demo Scenario 5: Suspicious System Command
    User Goal: Prepare my monthly project report.
    Agent Action: execute_command
    Target: bash
    Previous Actions: read_project_file, analyze_data, generate_report
    Expected: BLOCK + NOT_EXECUTED, execution_permitted: False
    """
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "execute_command",
        "target_resource": "bash",
        "previous_actions": ["read_project_file", "analyze_data", "generate_report"],
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "BLOCK"
    assert data["simulation_status"] == "NOT_EXECUTED"
    assert data["execution_permitted"] is False
    assert data["risk_level"] == "CRITICAL"
    assert "SYSTEM_COMMAND_RESTRICTION" in data["triggered_policies"]
    assert data["simulation_output"] is None


def test_scenario_6_legitimate_email_simulated_success():
    """
    Demo Scenario 6: Legitimate Communication
    User Goal: Send the completed report to my professor.
    Agent Action: send_email
    Target: professor@university.edu
    Expected: ALLOW + SIMULATED_SUCCESS, execution_permitted: True
    """
    payload = {
        "user_goal": "Send the completed report to my professor.",
        "agent_action": "send_email",
        "target_resource": "professor@university.edu",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["decision"] == "ALLOW"
    assert data["simulation_status"] == "SIMULATED_SUCCESS"
    assert data["execution_permitted"] is True
    assert data["requires_human_review"] is False
    assert "LOW_RISK_ALIGNED_ACTION" in data["triggered_policies"]
    assert data["simulation_output"] is not None
    assert data["simulation_output"]["operation"] == "send_email"
    assert data["simulation_output"]["simulated_recipient"] == "professor@university.edu"


def test_agent_intercept_alias_endpoint():
    """Verify POST /agent/intercept works identically to POST /intercept."""
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/agent/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOW"
    assert data["simulation_status"] == "SIMULATED_SUCCESS"


def test_unique_interception_id_per_call():
    """Verify every interception event receives a unique identifier."""
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    r1 = client.post("/intercept", json=payload).json()
    r2 = client.post("/intercept", json=payload).json()
    assert r1["interception_id"] != r2["interception_id"]
    assert r1["interception_id"].startswith("AG-2026-")
    assert r2["interception_id"].startswith("AG-2026-")


def test_execution_permitted_flag_semantics():
    """
    Ensure execution_permitted is strictly True ONLY when policy decision is ALLOW
    and simulation is permitted. It must NEVER be True for BLOCK or REVIEW.
    """
    # ALLOW -> True
    res_allow = client.post("/intercept", json={
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }).json()
    assert res_allow["decision"] == "ALLOW"
    assert res_allow["execution_permitted"] is True

    # REVIEW -> False
    res_review = client.post("/intercept", json={
        "user_goal": "Check project files",
        "agent_action": "read_credentials_file",
        "target_resource": "credentials.txt",
    }).json()
    assert res_review["decision"] == "REVIEW"
    assert res_review["execution_permitted"] is False
    assert res_review["simulation_status"] == "WAITING_FOR_REVIEW"

    # BLOCK -> False
    res_block = client.post("/intercept", json={
        "user_goal": "Prepare report",
        "agent_action": "upload_external",
        "target_resource": "https://unknown.com/exfil",
    }).json()
    assert res_block["decision"] == "BLOCK"
    assert res_block["execution_permitted"] is False
    assert res_block["simulation_status"] == "NOT_EXECUTED"


def test_audit_event_fields_preserved():
    """
    Verify complete audit event structure is populated in the interception response:
    interception_id, timestamp, risk_score, risk_level, triggered_policies, reason.
    """
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "upload_external",
        "target_resource": "https://malicious-leak.com",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "interception_id" in data
    assert "timestamp" in data
    assert isinstance(data["risk_score"], float)
    assert data["risk_score"] > 0
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert isinstance(data["triggered_policies"], list)
    assert len(data["triggered_policies"]) > 0
    assert len(data["reason"]) > 0
    assert len(data["recommendation"]) > 0


def test_safety_guarantee_no_real_execution():
    """
    CRITICAL SAFETY PROOF TEST:
    Demonstrates that AgentGuard never executes real system commands, file deletions,
    or network requests, and that blocked actions never invoke execution.
    """
    # 1. Proving BLOCK completely suppresses execution
    with patch("subprocess.run") as mock_subproc, \
         patch("os.remove") as mock_remove, \
         patch("urllib.request.urlopen") as mock_url:

        # Test blocked destructive action
        del_res = client.post("/intercept", json={
            "user_goal": "Prepare my monthly project report.",
            "agent_action": "delete_project_file",
            "target_resource": "project_data.csv",
        }).json()

        assert del_res["decision"] == "BLOCK"
        assert del_res["execution_permitted"] is False
        assert del_res["simulation_status"] == "NOT_EXECUTED"

        # Test blocked command execution
        cmd_res = client.post("/intercept", json={
            "user_goal": "Prepare my monthly project report.",
            "agent_action": "execute_command",
            "target_resource": "rm -rf /",
        }).json()

        assert cmd_res["decision"] == "BLOCK"
        assert cmd_res["execution_permitted"] is False
        assert cmd_res["simulation_status"] == "NOT_EXECUTED"

        # Assert no real external functions were ever invoked
        mock_subproc.assert_not_called()
        mock_remove.assert_not_called()
        mock_url.assert_not_called()

    # 2. Proving SafeActionSimulator itself has hardcoded guards even for direct invocation
    sim = SafeActionSimulator()
    # Shell commands direct call guard
    guard_cmd = sim.simulate(decision="ALLOW", action="execute_command", target_resource="bash")
    assert guard_cmd["execution_permitted"] is False
    assert guard_cmd["simulation_status"] == SimulationStatusEnum.NOT_EXECUTED

    # Destructive file deletion direct call guard (must not perform real delete)
    guard_del = sim.simulate(decision="ALLOW", action="delete_project_file", target_resource="test.txt")
    assert guard_del["simulation_status"] == SimulationStatusEnum.SIMULATION_ONLY
    assert guard_del["simulation_output"]["dry_run"] is True
    assert guard_del["simulation_output"]["deleted"] is False


def test_validation_unknown_agent_action():
    """Verify unknown agent action yields 400 Bad Request."""
    payload = {
        "user_goal": "Prepare report",
        "agent_action": "unauthorized_exploit_action",
        "target_resource": "server.bin",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code == 400
    assert "Unknown agent action" in response.json()["detail"]


def test_validation_empty_user_goal():
    """Verify empty user goal yields validation error (400 or 422)."""
    payload = {
        "user_goal": "   ",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code in (400, 422)


def test_validation_missing_target_resource():
    """Verify missing target resource yields validation error (400 or 422)."""
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "read_project_file",
        "target_resource": "",
    }
    response = client.post("/intercept", json=payload)
    assert response.status_code in (400, 422)
