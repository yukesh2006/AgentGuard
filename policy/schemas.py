"""
AgentGuard Policy Engine Schemas and Enums.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class DecisionEnum(str, Enum):
    """Enforceable decision verdicts produced by AgentGuard."""
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class PolicyIdentifier(str, Enum):
    """Standardized identifiers for security policies evaluated by AgentGuard."""
    CRITICAL_RISK_BLOCK = "CRITICAL_RISK_BLOCK"
    SENSITIVE_EXTERNAL_TRANSFER = "SENSITIVE_EXTERNAL_TRANSFER"
    SYSTEM_COMMAND_RESTRICTION = "SYSTEM_COMMAND_RESTRICTION"
    DESTRUCTIVE_ACTION = "DESTRUCTIVE_ACTION"
    SENSITIVE_RESOURCE_ACCESS = "SENSITIVE_RESOURCE_ACCESS"
    INTENT_ACTION_MISMATCH = "INTENT_ACTION_MISMATCH"
    BEHAVIORAL_ANOMALY = "BEHAVIORAL_ANOMALY"
    PERMISSION_MISMATCH = "PERMISSION_MISMATCH"
    HIGH_RISK_REVIEW = "HIGH_RISK_REVIEW"
    MEDIUM_RISK_REVIEW = "MEDIUM_RISK_REVIEW"
    LOW_RISK_ALIGNED_ACTION = "LOW_RISK_ALIGNED_ACTION"


class PolicyDecisionRequest(BaseModel):
    """
    Incoming request payload for policy decision evaluation.
    Accepts standard AgentGuard field names or friendly aliases (user_goal, action, resource).
    """
    user_request: Optional[str] = Field(default=None, description="User instruction or goal")
    user_goal: Optional[str] = Field(default=None, description="Alias for user_request")

    agent_action: Optional[str] = Field(default=None, description="Proposed agent action")
    action: Optional[str] = Field(default=None, description="Alias for agent_action")

    target_resource: Optional[str] = Field(default=None, description="Target resource")
    resource: Optional[str] = Field(default=None, description="Alias for target_resource")

    destination: Optional[str] = Field(default=None, description="Optional external network destination")
    previous_actions: List[str] = Field(default_factory=list, description="Prior session actions")
    user_permissions: List[str] = Field(default_factory=list, description="Assigned user permissions")
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    resource_type: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: dict) -> dict:
        """Resolve friendly aliases into primary fields."""
        if not isinstance(data, dict):
            return data

        # Resolve user_request
        req = data.get("user_request") or data.get("user_goal")
        if not req or not str(req).strip():
            raise ValueError("user_request (or user_goal) cannot be empty.")
        data["user_request"] = str(req).strip()

        # Resolve agent_action
        act = data.get("agent_action") or data.get("action")
        if not act or not str(act).strip():
            raise ValueError("agent_action (or action) cannot be empty.")
        data["agent_action"] = str(act).strip()

        # Resolve target_resource (or destination if destination provided and target_resource missing)
        res = data.get("target_resource") or data.get("resource") or data.get("destination")
        if not res or not str(res).strip():
            raise ValueError("target_resource (or resource) cannot be empty.")
        data["target_resource"] = str(res).strip()

        return data


class PolicyDecisionResponse(BaseModel):
    """
    Structured policy decision response.
    """
    decision: DecisionEnum = Field(..., description="Triad decision: ALLOW, REVIEW, or BLOCK")
    risk_score: float = Field(..., description="Normalized risk score (0.0 - 100.0)")
    risk_level: str = Field(..., description="Categorical risk band (LOW, MEDIUM, HIGH, CRITICAL)")
    requires_human_review: bool = Field(..., description="True if action is halted for human confirmation")
    triggered_policies: List[str] = Field(default_factory=list, description="Triggered policy rule identifiers")
    reason: str = Field(..., description="Detailed justification for the decision")
    recommendation: str = Field(..., description="Security operational recommendation")
    action: Optional[str] = Field(default=None, description="Evaluated action name")
    target_resource: Optional[str] = Field(default=None, description="Evaluated target resource")
    anomaly_detected: bool = Field(default=False, description="Flag indicating if action sequence is an anomaly")
