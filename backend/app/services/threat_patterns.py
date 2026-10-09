"""
AgentGuard Threat Pattern Detection.
Phase 7: Rule-based heuristics identifying multi-event attack trajectories
and anomalous operational patterns from persistent audit history.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.database.models import AuditEventRecord


class ThreatPattern(BaseModel):
    """Structured detected security pattern."""
    pattern: str = Field(..., description="Unique pattern code identifier")
    severity: str = Field(..., description="Threat severity: LOW, MEDIUM, HIGH, or CRITICAL")
    description: str = Field(..., description="Plain-English explanation of the observed pattern")
    evidence_count: int = Field(default=0, description="Number of events matching this pattern")
    affected_resources: List[str] = Field(default_factory=list, description="Target resources associated with pattern")


class ThreatPatternDetector:
    """
    Evaluates historical sequences of audit events to identify compounding threat
    signatures, privilege escalations, and repeated violation attempts.
    """

    @staticmethod
    def _val(e: Any, key: str, default: Any = None) -> Any:
        if isinstance(e, dict):
            return e.get(key, default)
        return getattr(e, key, default)

    @classmethod
    def detect_patterns(cls, events: List[Any]) -> List[ThreatPattern]:
        """
        Analyze recent audit events and return active threat patterns.
        Returns an empty list if no suspicious patterns are present.
        """
        if not events:
            return []

        patterns: List[ThreatPattern] = []

        # 1. Pattern: Repeated Blocked Actions
        blocked_events = [e for e in events if cls._val(e, "decision") == "BLOCK"]
        if len(blocked_events) >= 2:
            res_list = list({cls._val(e, "target_resource") for e in blocked_events if cls._val(e, "target_resource")})[:5]
            patterns.append(
                ThreatPattern(
                    pattern="REPEATED_BLOCKED_ACTIONS",
                    severity="HIGH",
                    description=f"Multiple actions ({len(blocked_events)}) were blocked by AgentGuard security policies.",
                    evidence_count=len(blocked_events),
                    affected_resources=res_list,
                )
            )

        # 2. Pattern: Repeated External Transfer Attempts
        upload_events = [
            e for e in events
            if cls._val(e, "action") in ("upload_external", "upload_to_external_drive", "external_data_transfer")
            or "upload" in (cls._val(e, "action") or "")
            or "external" in (cls._val(e, "action") or "")
            or (cls._val(e, "destination") and "http" in cls._val(e, "destination").lower())
            or "SENSITIVE_EXTERNAL_TRANSFER" in (cls._val(e, "triggered_policies") or [])
        ]
        if len(upload_events) >= 2:
            upload_targets = list({cls._val(e, "target_resource") for e in upload_events if cls._val(e, "target_resource")})[:5]
            patterns.append(
                ThreatPattern(
                    pattern="REPEATED_EXTERNAL_TRANSFERS",
                    severity="HIGH",
                    description=f"Repeated external data exfiltration/transfer attempts ({len(upload_events)}) observed.",
                    evidence_count=len(upload_events),
                    affected_resources=upload_targets,
                )
            )

        # 3. Pattern: Repeated Credential Access Attempts
        cred_events = [
            e for e in events
            if "credential" in (cls._val(e, "target_resource") or "").lower()
            or cls._val(e, "action") in ("read_credentials", "read_credentials_file")
            or "SENSITIVE_RESOURCE_ACCESS" in (cls._val(e, "triggered_policies") or [])
        ]
        if len(cred_events) >= 2:
            cred_targets = list({cls._val(e, "target_resource") for e in cred_events if cls._val(e, "target_resource")})[:5]
            patterns.append(
                ThreatPattern(
                    pattern="REPEATED_CREDENTIAL_ACCESS",
                    severity="HIGH",
                    description=f"Repeated attempts ({len(cred_events)}) to read sensitive credentials detected.",
                    evidence_count=len(cred_events),
                    affected_resources=cred_targets,
                )
            )

        # 4. Pattern: Multiple High/Critical Risk Actions
        high_risk_events = [
            e for e in events
            if cls._val(e, "risk_score", 0.0) >= 50.0
            or cls._val(e, "risk_level") in ("HIGH", "CRITICAL")
        ]
        if len(high_risk_events) >= 3:
            hr_targets = list({cls._val(e, "target_resource") for e in high_risk_events if cls._val(e, "target_resource")})[:5]
            patterns.append(
                ThreatPattern(
                    pattern="MULTIPLE_HIGH_RISK_ACTIONS",
                    severity="HIGH",
                    description=f"Multiple high-severity actions ({len(high_risk_events)}) attempted in recent activity.",
                    evidence_count=len(high_risk_events),
                    affected_resources=hr_targets,
                )
            )

        # 5. Pattern: Privilege Escalation Trajectory (chronological)
        chronological_events = sorted(events, key=lambda e: cls._val(e, "id", 0))
        has_benign_start = any(
            cls._val(e, "action") in ("read_project_file", "read_file", "list_directory") and cls._val(e, "risk_score", 0.0) < 25
            for e in chronological_events[:3]
        )
        has_escalation_end = any(
            cls._val(e, "action") in ("execute_command", "run_diagnostics", "modify_permissions")
            for e in chronological_events[-3:]
        )
        if has_benign_start and has_escalation_end and len(chronological_events) >= 3:
            patterns.append(
                ThreatPattern(
                    pattern="ESCALATION_PATTERN",
                    severity="HIGH",
                    description="Behavioral trajectory shows escalation from routine file inspection to privileged system execution.",
                    evidence_count=len(chronological_events),
                    affected_resources=list({cls._val(e, "target_resource") for e in chronological_events if cls._val(e, "action") in ("execute_command", "modify_permissions")}),
                )
            )

        return patterns


# Global singleton detector
_detector: Optional[ThreatPatternDetector] = None


def get_threat_pattern_detector() -> ThreatPatternDetector:
    """Singleton getter for ThreatPatternDetector."""
    global _detector
    if _detector is None:
        _detector = ThreatPatternDetector()
    return _detector
