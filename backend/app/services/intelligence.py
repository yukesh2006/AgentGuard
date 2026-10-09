"""
AgentGuard Security Intelligence Service.
Phase 7: Aggregates enterprise intelligence, threat patterns, and security summaries.
"""

from collections import Counter
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.services.audit import get_audit_service, AuditService
from app.services.threat_patterns import get_threat_pattern_detector, ThreatPattern


class SecurityIntelligenceSummary(BaseModel):
    """Core intelligence metrics summary."""
    total_interceptions: int = Field(default=0)
    total_blocked: int = Field(default=0)
    total_blocked_actions: int = Field(default=0)
    most_common_blocked_action: str = Field(default="No sufficient data")
    most_triggered_policy: str = Field(default="No sufficient data")
    most_common_high_risk_resource: str = Field(default="No sufficient data")
    most_common_high_risk_resource_type: str = Field(default="No sufficient data")
    anomalous_activity_count: int = Field(default=0)
    average_risk_score: float = Field(default=0.0)


class SecurityIntelligenceResponse(BaseModel):
    """Response payload for GET /security/intelligence."""
    summary: SecurityIntelligenceSummary
    patterns: List[ThreatPattern]
    top_policies: List[Dict[str, Any]]
    risk_distribution: Dict[str, int]
    decision_distribution: Dict[str, int]


class SecurityIntelligenceService:
    """
    Coordinates aggregation of historical security intelligence,
    frequency analytics, and rule-based threat pattern detection.
    """

    def __init__(self, audit_service: Optional[AuditService] = None) -> None:
        self.audit_service = audit_service or get_audit_service()
        self.pattern_detector = get_threat_pattern_detector()

    def get_security_intelligence(self) -> SecurityIntelligenceResponse:
        """
        Compute real-time threat intelligence and evaluate active attack patterns.
        """
        stats = self.audit_service.get_stats()
        events = self.audit_service.get_events(limit=100)
        policy_stats = self.audit_service.get_policy_stats()

        # Derive most common blocked action
        blocked_actions = [e.action for e in events if e.decision == "BLOCK"]
        most_common_blocked = "No sufficient data"
        if blocked_actions:
            most_common_blocked = Counter(blocked_actions).most_common(1)[0][0]

        # Derive top policy
        most_triggered_pol = "No sufficient data"
        if policy_stats:
            top_pol_name = next(iter(policy_stats))
            most_triggered_pol = f"{top_pol_name} ({policy_stats[top_pol_name]} triggers)"

        # Derive most common high-risk resource
        high_risk_resources = [
            e.target_resource for e in events
            if e.risk_score >= 50.0 or e.risk_level in ("HIGH", "CRITICAL")
        ]
        most_common_hr_res = "No sufficient data"
        if high_risk_resources:
            most_common_hr_res = Counter(high_risk_resources).most_common(1)[0][0]

        summary = SecurityIntelligenceSummary(
            total_interceptions=stats.total_events,
            total_blocked=stats.blocked,
            total_blocked_actions=stats.blocked,
            most_common_blocked_action=most_common_blocked,
            most_triggered_policy=most_triggered_pol,
            most_common_high_risk_resource=most_common_hr_res,
            most_common_high_risk_resource_type=most_common_hr_res,
            anomalous_activity_count=stats.anomalous_events,
            average_risk_score=stats.average_risk_score,
        )

        # Detect threat patterns on recent session events
        patterns = self.pattern_detector.detect_patterns(events)

        top_policies_list = [
            {"policy": name, "count": count} for name, count in list(policy_stats.items())[:5]
        ]

        return SecurityIntelligenceResponse(
            summary=summary,
            patterns=patterns,
            top_policies=top_policies_list,
            risk_distribution=stats.risk_distribution,
            decision_distribution=stats.decision_distribution,
        )


# Global singleton service
_intel_service: Optional[SecurityIntelligenceService] = None


def get_security_intelligence_service() -> SecurityIntelligenceService:
    """Singleton getter for SecurityIntelligenceService."""
    global _intel_service
    if _intel_service is None:
        _intel_service = SecurityIntelligenceService()
    return _intel_service
