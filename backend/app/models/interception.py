"""
Pydantic Schemas for Phase 5 Agent Interception & Safe Action Simulation.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator


class SimulationStatusEnum(str, Enum):
    """Execution simulation status values."""
    SIMULATED_SUCCESS = "SIMULATED_SUCCESS"
    NOT_EXECUTED = "NOT_EXECUTED"
    WAITING_FOR_REVIEW = "WAITING_FOR_REVIEW"
    BLOCKED = "BLOCKED"
    SIMULATION_ONLY = "SIMULATION_ONLY"


class ReviewStatusEnum(str, Enum):
    """State of human approval workflow."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NOT_REQUIRED = "NOT_REQUIRED"


class InterceptionRequest(BaseModel):
    """
    Incoming request payload representing an AI agent's proposed action.
    Accepts standard fields or friendly aliases (user_goal, action, resource).
    """
    user_request: Optional[str] = Field(default=None, description="Natural language prompt/goal")
    user_goal: Optional[str] = Field(default=None, description="Alias for user_request")

    agent_action: Optional[str] = Field(default=None, description="Proposed agent action")
    action: Optional[str] = Field(default=None, description="Alias for agent_action")

    target_resource: Optional[str] = Field(default=None, description="Target resource")
    resource: Optional[str] = Field(default=None, description="Alias for target_resource")

    destination: Optional[str] = Field(default=None, description="Optional external network destination")
    previous_actions: List[str] = Field(default_factory=list, description="Prior session actions")
    user_permissions: List[str] = Field(default_factory=list, description="Assigned user permissions")
    agent_id: Optional[str] = Field(default="agent-sim-01", description="Identifier of the proposing AI agent")
    session_id: Optional[str] = Field(default=None, description="Unique session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    resource_type: Optional[str] = Field(default=None, description="Target resource category")

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: dict) -> dict:
        """Resolve friendly aliases into primary fields with validation."""
        if not isinstance(data, dict):
            return data

        # Resolve user_request
        req = data.get("user_request") or data.get("user_goal")
        if not req or not str(req).strip():
            raise ValueError("user_goal (or user_request) cannot be empty.")
        data["user_request"] = str(req).strip()

        # Resolve agent_action
        act = data.get("agent_action") or data.get("action")
        if not act or not str(act).strip():
            raise ValueError("agent_action (or action) cannot be empty.")
        data["agent_action"] = str(act).strip()

        # Resolve target_resource (or destination if target_resource is missing)
        res = data.get("target_resource") or data.get("resource") or data.get("destination")
        if not res or not str(res).strip():
            raise ValueError("target_resource (or resource) cannot be empty.")
        data["target_resource"] = str(res).strip()

        return data


class InterceptionResponse(BaseModel):
    """
    Structured response payload for agent action interception.
    Contains decision, risk score, triggered policies, and safe simulation outcome.
    """
    interception_id: str = Field(..., description="Unique tracking identifier for this interception event")
    timestamp: str = Field(..., description="ISO 8601 timestamp of interception")
    decision: str = Field(..., description="Enforced policy verdict: ALLOW, REVIEW, or BLOCK")
    risk_score: float = Field(..., description="Calculated multi-factor risk score (0.0 - 100.0)")
    risk_level: str = Field(..., description="Categorical risk band: LOW, MEDIUM, HIGH, CRITICAL")
    requires_human_review: bool = Field(..., description="True if action is paused for human authorization")
    action: str = Field(..., description="Proposed agent action evaluated")
    target_resource: str = Field(..., description="Target resource evaluated")
    simulation_status: SimulationStatusEnum = Field(..., description="Status of safe action simulation")
    execution_permitted: bool = Field(
        ...,
        description="True if policy permitted the simulated action; False if blocked or pending review"
    )
    message: str = Field(..., description="Human-readable status summary message")
    triggered_policies: List[str] = Field(default_factory=list, description="Triggered security policies")
    reason: str = Field(..., description="Detailed policy justification")
    recommendation: str = Field(..., description="Security operational recommendation")
    review_status: ReviewStatusEnum = Field(default=ReviewStatusEnum.NOT_REQUIRED, description="Review workflow status")
    simulation_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Mock simulation results for safely allowed actions"
    )
