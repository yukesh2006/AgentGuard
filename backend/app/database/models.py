"""
AgentGuard Database & Audit Pydantic Models.
Phase 6: Audit Event Persistence & Statistics.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AuditEventRecord(BaseModel):
    """
    Structured persistent audit event record returned by the database/API.
    """
    id: int = Field(..., description="Unique auto-incrementing database primary key")
    interception_id: str = Field(..., description="Unique generated interception identifier")
    timestamp: str = Field(..., description="ISO 8601 event timestamp")
    user_goal: str = Field(..., description="Original user prompt or task goal")
    action: str = Field(..., description="Agent tool action proposed")
    target_resource: str = Field(..., description="Evaluated resource")
    destination: Optional[str] = Field(default=None, description="External endpoint destination if any")
    decision: str = Field(..., description="Security decision: ALLOW, REVIEW, or BLOCK")
    risk_score: float = Field(..., description="Normalized composite risk score (0-100)")
    risk_level: str = Field(..., description="Categorical risk tier: LOW, MEDIUM, HIGH, CRITICAL")
    explanation: str = Field(..., description="Detailed rationale explaining the decision")
    triggered_policies: List[str] = Field(default_factory=list, description="Security policies triggered")
    simulation_status: str = Field(..., description="Simulation outcome status")
    execution_permitted: bool = Field(..., description="Whether policy permitted execution/simulation")
    review_status: str = Field(..., description="Human review state")
    anomaly_detected: bool = Field(default=False, description="Whether behavioral anomaly was flagged")
    intent_similarity: Optional[float] = Field(default=None, description="Semantic consistency score")
    simulation_output: Optional[Dict[str, Any]] = Field(default=None, description="Mock simulation output")


class AuditEventCreate(BaseModel):
    """
    Input model for creating a new persistent audit event.
    """
    interception_id: str
    timestamp: str
    user_goal: str
    action: str
    target_resource: str
    destination: Optional[str] = None
    decision: str
    risk_score: float
    risk_level: str
    explanation: str
    triggered_policies: List[str]
    simulation_status: str
    execution_permitted: bool
    review_status: str
    anomaly_detected: bool = False
    intent_similarity: Optional[float] = None
    simulation_output: Optional[Dict[str, Any]] = None


class AuditStatsResponse(BaseModel):
    """
    Summary metrics and distributions for the security dashboard.
    """
    total_events: int = Field(default=0, description="Total count of intercepted events")
    allowed: int = Field(default=0, description="Count of ALLOW decisions")
    review: int = Field(default=0, description="Count of REVIEW decisions")
    blocked: int = Field(default=0, description="Count of BLOCK decisions")
    average_risk_score: float = Field(default=0.0, description="Mean risk score across all events")
    high_risk_events: int = Field(default=0, description="Count of HIGH risk events")
    critical_events: int = Field(default=0, description="Count of CRITICAL risk events")
    anomalous_events: int = Field(default=0, description="Count of events flagged as behavioral anomalies")
    risk_distribution: Dict[str, int] = Field(
        default_factory=lambda: {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
        description="Event breakdown across risk bands",
    )
    decision_distribution: Dict[str, int] = Field(
        default_factory=lambda: {"ALLOW": 0, "REVIEW": 0, "BLOCK": 0},
        description="Event breakdown across decision verdicts",
    )
