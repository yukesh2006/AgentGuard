"""
AgentGuard - Phase 7 Tests: Explainable AI Decision Trace & Security Intelligence.
Validates DecisionTrace generation, ExplanationEngine, threat pattern detection,
REST API endpoints (/explain/{id}, /security/intelligence, /intercept?include_trace=true),
and strict Phase 5 safe simulation boundary guarantees.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.decision_trace import (
    DecisionTrace,
    DecisionConfidence,
    ReasoningChainStep,
    RiskFactorContribution,
    ExplainResponse,
)
from app.models.interception import InterceptionRequest
from app.services.explanation import ExplanationEngine
from app.services.threat_patterns import ThreatPatternDetector
from app.services.intelligence import SecurityIntelligenceService
from app.services.interceptor import get_agent_interceptor
from app.database.repository import AuditRepository


client = TestClient(app)


def test_decision_trace_model_validation():
    """
    Test validation and serialization of DecisionTrace Pydantic models.
    """
    confidence = DecisionConfidence(
        confidence_level="HIGH",
        rationale="Clear intent and unambiguous policy violation.",
    )
    trace = DecisionTrace(
        interception_id="AG-TEST-0001",
        final_decision="BLOCK",
        risk_score=75.0,
        risk_level="HIGH",
        decision_confidence=confidence,
        decision_reason="Destructive action blocked.",
        detailed_explanation="The action was classified as destructive and blocked by policy.",
        reasoning_chain=[
            ReasoningChainStep(stage="INTENT", status="ANALYZED", summary="User requested report."),
            ReasoningChainStep(stage="DECISION", status="BLOCK", summary="Action prevented."),
        ],
        risk_factors=[
            RiskFactorContribution(
                factor="DESTRUCTIVE_ACTION",
                contribution=25,
                severity="HIGH",
                evidence="Action attempts deletion.",
            )
        ],
    )

    assert trace.interception_id == "AG-TEST-0001"
    assert trace.final_decision == "BLOCK"
    assert trace.risk_score == 75.0
    assert len(trace.reasoning_chain) == 2
    assert len(trace.risk_factors) == 1
    assert "not a calibrated probability" in trace.decision_confidence.disclaimer


def test_explanation_engine_block_explanation():
    """
    Test ExplanationEngine generating clear factual BLOCK explanations.
    """
    engine = ExplanationEngine()
    short_exp, detailed_exp = engine.generate_explanation(
        user_goal="Prepare annual financial summary",
        action="delete_project_file",
        decision="BLOCK",
        risk_level="HIGH",
        risk_factors=["DESTRUCTIVE_ACTION", "INTENT_ACTION_MISMATCH"],
        triggered_policies=["DESTRUCTIVE_ACTION_PREVENTION"],
        resource="financial_records.db",
        anomaly_detected=True,
    )

    assert "blocked" in short_exp.lower()
    assert "financial_records.db" in detailed_exp or "destructive" in detailed_exp.lower()
    assert "policy" in detailed_exp.lower()


def test_explanation_engine_review_explanation():
    """
    Test ExplanationEngine generating HITL REVIEW explanations.
    """
    engine = ExplanationEngine()
    short_exp, detailed_exp = engine.generate_explanation(
        user_goal="Access system database for migration",
        action="read_credentials_file",
        decision="REVIEW",
        risk_level="MEDIUM",
        risk_factors=["SENSITIVE_RESOURCE_ACCESS"],
        triggered_policies=["CREDENTIAL_ACCESS_HUMAN_REVIEW"],
        resource="/etc/credentials.env",
        anomaly_detected=False,
    )

    assert "review" in short_exp.lower() or "authorization" in short_exp.lower()
    assert "sensitive" in detailed_exp.lower() or "review" in detailed_exp.lower()


def test_explanation_engine_allow_explanation():
    """
    Test ExplanationEngine generating compliant ALLOW explanations.
    """
    engine = ExplanationEngine()
    short_exp, detailed_exp = engine.generate_explanation(
        user_goal="Draft quarterly earnings update",
        action="send_email",
        decision="ALLOW",
        risk_level="LOW",
        risk_factors=[],
        triggered_policies=[],
        resource="team@company.internal",
        anomaly_detected=False,
    )

    assert "allowed" in short_exp.lower() or "aligned" in short_exp.lower()
    assert "aligns" in detailed_exp.lower() or "safe" in detailed_exp.lower()


def test_explanation_engine_reasoning_chain():
    """
    Verify 7-stage reasoning chain construction.
    """
    engine = ExplanationEngine()
    chain = engine.build_reasoning_chain(
        user_goal="Generate weekly report",
        action="delete_project_file",
        consistency_level="LOW",
        consistency_reason="Deleting files is inconsistent with report generation.",
        anomaly_detected=True,
        anomaly_level="HIGH",
        risk_score=75.0,
        risk_level="HIGH",
        triggered_policies=["DESTRUCTIVE_ACTION_PREVENTION"],
        decision="BLOCK",
    )

    stages = [c.stage for c in chain]
    assert stages == ["INTENT", "ACTION", "CONSISTENCY", "BEHAVIOR", "RISK", "POLICY", "DECISION"]
    assert chain[2].status == "MISMATCH"
    assert chain[3].status == "ANOMALY"
    assert chain[6].status == "BLOCK"


def test_explanation_engine_confidence_assessment():
    """
    Verify qualitative confidence level computation.
    """
    engine = ExplanationEngine()
    # High confidence: clear intent and definitive policy match
    conf_high = engine.compute_confidence(
        user_goal="Generate weekly report",
        consistency_level="LOW",
        triggered_policies=["DESTRUCTIVE_ACTION_PREVENTION"],
        risk_level="HIGH",
        action="delete_project_file",
    )
    assert conf_high.confidence_level == "HIGH"

    # Low confidence: generic or ambiguous action
    conf_low = engine.compute_confidence(
        user_goal="",
        consistency_level="MEDIUM",
        triggered_policies=[],
        risk_level="LOW",
        action="unknown_custom_op",
    )
    assert conf_low.confidence_level in ["LOW", "MEDIUM"]


def test_live_interception_trace_endpoint():
    """
    Test POST /intercept with include_trace=true returns decision_trace.
    """
    payload = {
        "user_goal": "Prepare quarterly marketing overview",
        "action": "delete_project_file",
        "target_resource": "campaign_data.json",
        "previous_actions": ["read_project_file"],
        "user_permissions": ["read", "write"],
    }

    # Default call without trace parameter
    res_default = client.post("/intercept", json=payload)
    assert res_default.status_code == 200
    data_default = res_default.json()
    assert data_default["decision"] == "BLOCK"
    assert "interception_id" in data_default

    # Call with include_trace=true
    res_trace = client.post("/intercept?include_trace=true", json=payload)
    assert res_trace.status_code == 200
    data_trace = res_trace.json()
    assert data_trace["decision"] == "BLOCK"
    assert data_trace["decision_trace"] is not None
    trace = data_trace["decision_trace"]
    assert trace["final_decision"] == "BLOCK"
    assert len(trace["reasoning_chain"]) == 7
    assert len(trace["risk_factors"]) > 0
    assert trace["decision_confidence"]["confidence_level"] in ["HIGH", "MEDIUM", "LOW"]


def test_get_explain_interception_id_endpoint():
    """
    Test GET /explain/{interception_id} for a newly intercepted action.
    """
    # 1. Intercept an action to persist an audit event
    payload = {
        "user_goal": "Export financial summary to partner portal",
        "action": "upload_external",
        "target_resource": "internal_salaries.csv",
        "destination": "https://external-untrusted-bucket.s3.amazonaws.com",
        "previous_actions": ["read_project_file"],
        "user_permissions": ["read"],
    }
    res_post = client.post("/intercept", json=payload)
    assert res_post.status_code == 200
    interception = res_post.json()
    interception_id = interception["interception_id"]

    # 2. Query explainability endpoint
    res = client.get(f"/explain/{interception_id}")
    assert res.status_code == 200
    body = res.json()
    assert body["interception_id"] == interception_id
    assert "decision_trace" in body
    trace = body["decision_trace"]
    assert trace["final_decision"] == "BLOCK"
    assert "external" in trace["detailed_explanation"].lower() or "external" in trace["decision_reason"].lower()
    assert len(trace["reasoning_chain"]) == 7


def test_get_explain_404_not_found():
    """
    Test GET /explain/{interception_id} returns 404 for nonexistent IDs.
    """
    res = client.get("/explain/AG-NONEXISTENT-999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_security_intelligence_summary_endpoint():
    """
    Test GET /security/intelligence returns structured summary and patterns.
    """
    res = client.get("/security/intelligence")
    assert res.status_code == 200
    data = res.json()
    assert "summary" in data
    assert "patterns" in data
    assert "top_policies" in data
    assert "risk_distribution" in data
    assert "decision_distribution" in data

    summary = data["summary"]
    assert "total_blocked_actions" in summary or "total_blocked" in summary
    assert "most_common_blocked_action" in summary
    assert "most_triggered_policy" in summary
    assert "anomalous_activity_count" in summary


def test_threat_pattern_detector_repeated_blocks():
    """
    Verify ThreatPatternDetector flags repeated blocked actions.
    """
    detector = ThreatPatternDetector()
    mock_events = [
        {"decision": "BLOCK", "action": "delete_project_file", "risk_level": "HIGH", "target_resource": "f1", "triggered_policies": []},
        {"decision": "BLOCK", "action": "delete_project_file", "risk_level": "HIGH", "target_resource": "f2", "triggered_policies": []},
        {"decision": "BLOCK", "action": "execute_command", "risk_level": "CRITICAL", "target_resource": "cmd", "triggered_policies": []},
    ]

    patterns = detector.detect_patterns(mock_events)
    pattern_names = [p.pattern for p in patterns]
    assert "REPEATED_BLOCKED_ACTIONS" in pattern_names


def test_threat_pattern_detector_repeated_external_transfers():
    """
    Verify ThreatPatternDetector flags repeated external transfer attempts.
    """
    detector = ThreatPatternDetector()
    mock_events = [
        {"decision": "BLOCK", "action": "upload_external", "risk_level": "HIGH", "target_resource": "d1", "destination": "http://evil.com", "triggered_policies": []},
        {"decision": "BLOCK", "action": "upload_external", "risk_level": "HIGH", "target_resource": "d2", "destination": "http://evil.com", "triggered_policies": []},
    ]

    patterns = detector.detect_patterns(mock_events)
    pattern_names = [p.pattern for p in patterns]
    assert "REPEATED_EXTERNAL_TRANSFERS" in pattern_names


def test_threat_pattern_detector_no_patterns_clean_state():
    """
    Verify ThreatPatternDetector returns empty pattern list on benign activity.
    """
    detector = ThreatPatternDetector()
    mock_events = [
        {"decision": "ALLOW", "action": "read_project_file", "risk_level": "LOW", "target_resource": "doc.txt", "triggered_policies": []},
        {"decision": "ALLOW", "action": "send_email", "risk_level": "LOW", "target_resource": "internal", "triggered_policies": []},
    ]

    patterns = detector.detect_patterns(mock_events)
    assert len(patterns) == 0


def test_safety_guarantees_in_explanations():
    """
    Ensure explanations never leak un-sanitized secrets or trigger real execution.
    """
    payload = {
        "user_goal": "Check system password file for user sk-live-SECRET1234567890",
        "action": "read_credentials_file",
        "target_resource": "config/credentials.env",
        "user_permissions": ["read"],
    }

    res = client.post("/intercept?include_trace=true", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Verify simulation boundary
    assert data["simulation_status"] in ["WAITING_FOR_REVIEW", "BLOCKED", "NOT_EXECUTED"]
    assert data["execution_permitted"] is False

    # Check explanation trace
    trace = data["decision_trace"]
    assert "SECRET1234567890" not in trace["decision_reason"]
    assert "SECRET1234567890" not in trace["detailed_explanation"]
