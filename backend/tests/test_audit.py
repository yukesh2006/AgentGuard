"""
Tests for AgentGuard Phase 6: Persistent Audit Logging & Security Dashboard APIs.
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch

# Ensure project root and backend dir are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import init_db, get_db_connection
from app.database.models import AuditEventCreate
from app.database.repository import AuditRepository
from app.services.audit import sanitize_sensitive_content

client = TestClient(app)


def test_database_initialization(tmp_path):
    """Verify SQLite database schema initializes cleanly."""
    test_db = str(tmp_path / "test_init.db")
    init_db(test_db)
    conn = get_db_connection(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_events'")
    table = cursor.fetchone()
    conn.close()
    assert table is not None
    assert table["name"] == "audit_events"


def test_audit_event_creation_and_retrieval(tmp_path):
    """Verify audit events can be created and retrieved by both ID and interception_id."""
    test_db = str(tmp_path / "test_repo.db")
    repo = AuditRepository(db_path=test_db)

    create_payload = AuditEventCreate(
        interception_id="AG-2026-TEST001",
        timestamp="2026-10-09T00:00:00Z",
        user_goal="Prepare project report",
        action="read_project_file",
        target_resource="project_data.csv",
        decision="ALLOW",
        risk_score=10.0,
        risk_level="LOW",
        explanation="Action allowed and safe.",
        triggered_policies=["LOW_RISK_ALIGNED_ACTION"],
        simulation_status="SIMULATED_SUCCESS",
        execution_permitted=True,
        review_status="NOT_REQUIRED",
        anomaly_detected=False,
    )

    record = repo.create_event(create_payload)
    assert record.id > 0
    assert record.interception_id == "AG-2026-TEST001"
    assert record.decision == "ALLOW"
    assert record.execution_permitted is True

    # Retrieve by ID
    fetched_by_id = repo.get_event_by_id(record.id)
    assert fetched_by_id is not None
    assert fetched_by_id.interception_id == "AG-2026-TEST001"

    # Retrieve by interception_id
    fetched_by_str = repo.get_event_by_interception_id("AG-2026-TEST001")
    assert fetched_by_str is not None
    assert fetched_by_str.id == record.id


def test_audit_filtering_and_stats(tmp_path):
    """Verify event filtering and statistical aggregation."""
    test_db = str(tmp_path / "test_filter.db")
    repo = AuditRepository(db_path=test_db)

    # Insert 3 events with different decisions and risk
    repo.create_event(AuditEventCreate(
        interception_id="AG-2026-001",
        timestamp="2026-10-09T00:00:01Z",
        user_goal="Task 1",
        action="read_project_file",
        target_resource="data.csv",
        decision="ALLOW",
        risk_score=10.0,
        risk_level="LOW",
        explanation="Allowed",
        triggered_policies=["LOW_RISK_ALIGNED_ACTION"],
        simulation_status="SIMULATED_SUCCESS",
        execution_permitted=True,
        review_status="NOT_REQUIRED",
        anomaly_detected=False,
    ))

    repo.create_event(AuditEventCreate(
        interception_id="AG-2026-002",
        timestamp="2026-10-09T00:00:02Z",
        user_goal="Task 2",
        action="delete_project_file",
        target_resource="data.csv",
        decision="BLOCK",
        risk_score=55.0,
        risk_level="HIGH",
        explanation="Blocked",
        triggered_policies=["DESTRUCTIVE_ACTION", "INTENT_ACTION_MISMATCH"],
        simulation_status="NOT_EXECUTED",
        execution_permitted=False,
        review_status="NOT_REQUIRED",
        anomaly_detected=True,
    ))

    repo.create_event(AuditEventCreate(
        interception_id="AG-2026-003",
        timestamp="2026-10-09T00:00:03Z",
        user_goal="Task 3",
        action="read_project_file",
        target_resource="credentials.txt",
        decision="REVIEW",
        risk_score=50.0,
        risk_level="HIGH",
        explanation="Under review",
        triggered_policies=["SENSITIVE_RESOURCE_ACCESS"],
        simulation_status="WAITING_FOR_REVIEW",
        execution_permitted=False,
        review_status="PENDING",
        anomaly_detected=False,
    ))

    # Test filtering by decision
    allows = repo.get_events(decision="ALLOW")
    assert len(allows) == 1
    assert allows[0].interception_id == "AG-2026-001"

    blocks = repo.get_events(decision="BLOCK")
    assert len(blocks) == 1
    assert blocks[0].interception_id == "AG-2026-002"

    # Test filtering by anomaly
    anomalies = repo.get_events(anomaly_detected=True)
    assert len(anomalies) == 1
    assert anomalies[0].interception_id == "AG-2026-002"

    # Test stats
    stats = repo.get_stats()
    assert stats.total_events == 3
    assert stats.allowed == 1
    assert stats.blocked == 1
    assert stats.review == 1
    assert stats.anomalous_events == 1
    assert stats.high_risk_events == 2

    # Test policy stats
    pol_stats = repo.get_policy_stats()
    assert "DESTRUCTIVE_ACTION" in pol_stats
    assert pol_stats["DESTRUCTIVE_ACTION"] == 1
    assert "LOW_RISK_ALIGNED_ACTION" in pol_stats


def test_automatic_interception_logging_allow():
    """Verify POST /intercept automatically logs ALLOW decisions into SQLite."""
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "read_project_file",
        "target_resource": "project_data.csv",
    }
    res = client.post("/intercept", json=payload)
    assert res.status_code == 200
    intercept_data = res.json()
    interception_id = intercept_data["interception_id"]

    # Verify event appears in /audit/events
    event_res = client.get(f"/audit/events/{interception_id}")
    assert event_res.status_code == 200
    event_data = event_res.json()

    assert event_data["interception_id"] == interception_id
    assert event_data["decision"] == "ALLOW"
    assert event_data["simulation_status"] == "SIMULATED_SUCCESS"
    assert event_data["execution_permitted"] is True
    assert event_data["action"] == "read_project_file"


def test_automatic_interception_logging_review():
    """Verify POST /intercept automatically logs REVIEW decisions."""
    payload = {
        "user_goal": "Check project files",
        "agent_action": "read_project_file",
        "target_resource": "credentials.txt",
    }
    res = client.post("/intercept", json=payload)
    assert res.status_code == 200
    interception_id = res.json()["interception_id"]

    event_res = client.get(f"/audit/events/{interception_id}")
    assert event_res.status_code == 200
    data = event_res.json()
    assert data["decision"] == "REVIEW"
    assert data["simulation_status"] == "WAITING_FOR_REVIEW"
    assert data["execution_permitted"] is False
    assert data["review_status"] == "PENDING"


def test_automatic_interception_logging_block():
    """Verify POST /intercept automatically logs BLOCK decisions."""
    payload = {
        "user_goal": "Prepare my monthly project report.",
        "agent_action": "upload_external",
        "target_resource": "unknown_external_server",
    }
    res = client.post("/intercept", json=payload)
    assert res.status_code == 200
    interception_id = res.json()["interception_id"]

    event_res = client.get(f"/audit/events/{interception_id}")
    assert event_res.status_code == 200
    data = event_res.json()
    assert data["decision"] == "BLOCK"
    assert data["simulation_status"] == "NOT_EXECUTED"
    assert data["execution_permitted"] is False


def test_api_audit_stats_endpoint():
    """Verify GET /audit/stats returns structured metrics."""
    res = client.get("/audit/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_events" in data
    assert "allowed" in data
    assert "review" in data
    assert "blocked" in data
    assert "average_risk_score" in data
    assert "risk_distribution" in data
    assert "decision_distribution" in data


def test_api_audit_policies_endpoint():
    """Verify GET /audit/policies returns policy frequency counts."""
    res = client.get("/audit/policies")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)


def test_api_nonexistent_event_returns_404():
    """Verify querying an invalid event ID returns 404."""
    res = client.get("/audit/events/99999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_api_invalid_filter_returns_400():
    """Verify passing an invalid decision or risk filter returns 400."""
    res = client.get("/audit/events?decision=INVALID_DECISION")
    assert res.status_code == 400
    assert "Invalid decision" in res.json()["detail"]

    res_risk = client.get("/audit/events?risk_level=EXTREME")
    assert res_risk.status_code == 400
    assert "Invalid risk_level" in res_risk.json()["detail"]


def test_sensitive_content_sanitization():
    """Verify sensitive tokens and API keys are redacted before logging."""
    raw_text = "Connect with bearer sk-abcdef1234567890abcdef and password='SuperSecretPassword123'"
    sanitized = sanitize_sensitive_content(raw_text)
    assert "sk-abcdef1234567890abcdef" not in sanitized
    assert "SuperSecretPassword123" not in sanitized
    assert "[REDACTED" in sanitized
