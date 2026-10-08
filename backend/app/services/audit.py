"""
AgentGuard Audit Service.
Phase 6: Business logic for security audit logging, sanitization, and querying.
"""

import re
from typing import List, Optional, Dict, Any
from app.database.repository import get_audit_repository, AuditRepository
from app.database.models import AuditEventRecord, AuditEventCreate, AuditStatsResponse

# Sanitization patterns for sensitive data masking in audit logs
SENSITIVE_PATTERNS = [
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9_\-\.]{15,}"), r"\1[REDACTED_TOKEN]"),
    (re.compile(r"(?i)\b(sk-[a-zA-Z0-9]{16,})\b"), r"[REDACTED_API_KEY]"),
    (re.compile(r"(?i)\b(password|passwd|secret|api_key|access_token)\s*[:=]\s*['\"]?([^\s'\",]{4,})['\"]?"), r"\1=[REDACTED]"),
]


def sanitize_sensitive_content(text: Optional[str]) -> Optional[str]:
    """
    Mask potential secrets, API keys, or raw bearer tokens
    before writing to persistent logs.
    """
    if not text:
        return text

    sanitized = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


class AuditService:
    """
    Service coordinating persistent audit logging and sanitized dashboard queries.
    """

    def __init__(self, repository: Optional[AuditRepository] = None) -> None:
        self.repository = repository or get_audit_repository()

    def log_interception(
        self,
        interception_id: str,
        timestamp: str,
        user_goal: str,
        action: str,
        target_resource: str,
        destination: Optional[str],
        decision: str,
        risk_score: float,
        risk_level: str,
        explanation: str,
        triggered_policies: List[str],
        simulation_status: str,
        execution_permitted: bool,
        review_status: str,
        anomaly_detected: bool = False,
        intent_similarity: Optional[float] = None,
        simulation_output: Optional[Dict[str, Any]] = None,
    ) -> AuditEventRecord:
        """
        Sanitize and persist an interception event to the audit database.
        """
        sanitized_goal = sanitize_sensitive_content(user_goal) or ""
        sanitized_resource = sanitize_sensitive_content(target_resource) or ""
        sanitized_dest = sanitize_sensitive_content(destination)

        event_create = AuditEventCreate(
            interception_id=interception_id,
            timestamp=timestamp,
            user_goal=sanitized_goal,
            action=action,
            target_resource=sanitized_resource,
            destination=sanitized_dest,
            decision=decision,
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=explanation,
            triggered_policies=triggered_policies,
            simulation_status=simulation_status,
            execution_permitted=execution_permitted,
            review_status=review_status,
            anomaly_detected=anomaly_detected,
            intent_similarity=intent_similarity,
            simulation_output=simulation_output,
        )

        return self.repository.create_event(event_create)

    def get_events(
        self,
        limit: int = 50,
        offset: int = 0,
        decision: Optional[str] = None,
        risk_level: Optional[str] = None,
        anomaly_detected: Optional[bool] = None,
    ) -> List[AuditEventRecord]:
        """Fetch filtered audit events."""
        return self.repository.get_events(
            limit=limit,
            offset=offset,
            decision=decision,
            risk_level=risk_level,
            anomaly_detected=anomaly_detected,
        )

    def get_event_by_id(self, identifier: str) -> Optional[AuditEventRecord]:
        """Fetch event by auto-increment ID or string interception_id."""
        if identifier.isdigit():
            event = self.repository.get_event_by_id(int(identifier))
            if event:
                return event
        return self.repository.get_event_by_interception_id(identifier)

    def get_stats(self) -> AuditStatsResponse:
        """Fetch dashboard statistics."""
        return self.repository.get_stats()

    def get_policy_stats(self) -> Dict[str, int]:
        """Fetch frequency counts for triggered policies."""
        return self.repository.get_policy_stats()


# Singleton service instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Singleton getter for AuditService."""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service
