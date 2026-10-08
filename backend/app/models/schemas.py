"""
Pydantic Schemas for AgentGuard API Requests and Responses.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """
    Incoming request payload for AgentGuard analysis.
    """
    user_request: str = Field(
        ...,
        description="Natural language instruction or prompt given by the user",
        examples=["Prepare my monthly project report"],
    )
    agent_action: str = Field(
        ...,
        description="The action identifier the AI agent attempts to execute",
        examples=["read_project_file"],
    )
    target_resource: str = Field(
        ...,
        description="The target file, endpoint, or system resource the action acts upon",
        examples=["project_data.csv"],
    )

    # Optional contextual attributes
    session_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for the active agent session",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Identifier of the user requesting the operation",
    )
    resource_type: Optional[str] = Field(
        default=None,
        description="Explicit classification of the target resource (e.g., file, network, database)",
    )
    previous_actions: List[str] = Field(
        default_factory=list,
        description="List of prior actions executed in this session",
    )
    user_permissions: List[str] = Field(
        default_factory=list,
        description="Permissions or roles assigned to the user",
    )

    @field_validator("user_request")
    @classmethod
    def validate_user_request(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("user_request cannot be empty or blank")
        return trimmed

    @field_validator("agent_action")
    @classmethod
    def validate_agent_action(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("agent_action cannot be empty or blank")
        return trimmed

    @field_validator("target_resource")
    @classmethod
    def validate_target_resource(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("target_resource cannot be empty or blank")
        return trimmed


class IntentResult(BaseModel):
    """Structured representation of extracted user intent."""
    intent: str = Field(..., description="Classified intent category")
    goal: str = Field(..., description="Extracted user goal description")
    confidence: float = Field(..., description="Computed ML confidence score")


class ContextResult(BaseModel):
    """Structured representation of operational context."""
    goal: str = Field(..., description="Primary user goal")
    resource: str = Field(..., description="Target resource being accessed")
    action: str = Field(..., description="Action being performed")
    resource_type: str = Field(..., description="Categorized resource type")
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    previous_actions: List[str] = Field(default_factory=list)
    user_permissions: List[str] = Field(default_factory=list)


class ActionInfo(BaseModel):
    """Normalized action details."""
    name: str = Field(..., description="Standardized action name")
    description: str = Field(..., description="Human-readable action description")


class ConsistencyResult(BaseModel):
    """Intent-Action consistency analysis result."""
    similarity_score: float = Field(..., description="Calculated cosine similarity score")
    compatibility: str = Field(..., description="Compatibility category: high, medium, or low")


class SecuritySignal(BaseModel):
    """Contextual security signal."""
    type: str = Field(..., description="Signal identifier type")
    severity: str = Field(..., description="Severity level: low, medium, or high")
    description: str = Field(..., description="Human-readable explanation of the signal")


class AnalyzeResponse(BaseModel):
    """Full response schema for POST /analyze endpoint."""
    intent: IntentResult
    context: ContextResult
    action: ActionInfo
    consistency: ConsistencyResult
    signals: List[SecuritySignal] = Field(default_factory=list)
