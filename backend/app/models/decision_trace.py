"""
AgentGuard Decision Trace & Explainability Models.
Phase 7: Structured representations of the evidence chain and security intelligence.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class IntentAnalysisTrace(BaseModel):
    """Semantic intent analysis evidence."""
    user_goal: str = Field(..., description="Stated goal or prompt of the user")
    detected_intent: str = Field(..., description="Classified intent category")
    intent_action_similarity: float = Field(..., description="Cosine similarity score (0.0 - 1.0)")
    consistency_level: str = Field(..., description="Consistency rating: HIGH, MEDIUM, or LOW")
    consistency_reason: str = Field(..., description="Natural language semantic rationale")


class ContextAnalysisTrace(BaseModel):
    """Operational context and environment evidence."""
    context_summary: str = Field(..., description="Summary of operational context")
    previous_action_count: int = Field(default=0, description="Count of prior actions in trajectory")
    context_consistent: bool = Field(default=True, description="Whether session context is aligned")
    resource_type: str = Field(..., description="Categorized resource type")


class BehaviorAnalysisTrace(BaseModel):
    """Behavioral trajectory and anomaly detection evidence."""
    anomaly_detected: bool = Field(default=False, description="Whether IsolationForest flagged an outlier")
    anomaly_level: str = Field(..., description="Severity tier: NONE, LOW, MEDIUM, or HIGH")
    behavioral_reason: str = Field(..., description="Rationale for behavioral categorization")
    anomaly_score: Optional[float] = Field(default=None, description="Raw IsolationForest anomaly score")


class ResourceAnalysisTrace(BaseModel):
    """Target asset classification and sensitivity evidence."""
    resource: str = Field(..., description="Target resource string or endpoint")
    resource_type: str = Field(..., description="Type of target resource")
    sensitivity: str = Field(..., description="Sensitivity tier: NORMAL, SENSITIVE, or CRITICAL")
    category: str = Field(..., description="Functional classification category")


class RiskFactorContribution(BaseModel):
    """Individual contributing factor to the aggregate multi-factor risk score."""
    factor: str = Field(..., description="Standardized factor name")
    contribution: float = Field(..., description="Points added to total risk score")
    severity: str = Field(..., description="Factor severity: LOW, MEDIUM, HIGH, or CRITICAL")
    evidence: str = Field(..., description="Factual evidence supporting this risk contribution")


class PolicyAnalysisTrace(BaseModel):
    """Security policy evaluation evidence."""
    triggered_policies: List[str] = Field(default_factory=list, description="Triggered policy rule identifiers")
    policy_reasons: List[str] = Field(default_factory=list, description="Explanations for each triggered rule")


class ReasoningChainStep(BaseModel):
    """Single step in the end-to-end security decision reasoning chain."""
    stage: str = Field(..., description="Stage name: INTENT, ACTION, CONSISTENCY, BEHAVIOR, RISK, POLICY, DECISION")
    status: str = Field(..., description="Stage status verdict")
    summary: str = Field(..., description="Summary of evidence evaluated at this stage")


class SafetyActionTrace(BaseModel):
    """Simulation status and execution containment boundaries."""
    simulation_status: str = Field(..., description="Simulation outcome status")
    execution_permitted: bool = Field(..., description="Whether action was permitted to simulate")


class DecisionConfidence(BaseModel):
    """
    Qualitative indicator of evidence completeness and signal consistency.
    Note: Decision confidence represents the completeness and consistency of
    AgentGuard's available signals; it is not a calibrated probability of safety.
    """
    confidence_level: str = Field(default="HIGH", description="Confidence rating: HIGH, MEDIUM, or LOW")
    level: Optional[str] = Field(default=None, description="Alias for confidence_level")
    rationale: str = Field(default="Evidence completeness evaluated.", description="Rationale for confidence classification")
    reason: Optional[str] = Field(default=None, description="Alias for rationale")
    signals_completeness: float = Field(default=1.0, description="Completeness ratio of evaluated signals (0.0 - 1.0)")
    disclaimer: str = Field(
        default="Decision confidence represents the completeness and consistency of AgentGuard's available signals. It is not a calibrated probability of safety.",
        description="Standard disclaimer regarding qualitative metric",
    )

    def model_post_init(self, __context: Any) -> None:
        if self.level and not self.confidence_level:
            self.confidence_level = self.level
        elif self.confidence_level and not self.level:
            self.level = self.confidence_level
        if self.reason and (self.rationale == "Evidence completeness evaluated." or not self.rationale):
            self.rationale = self.reason
        elif self.rationale and not self.reason:
            self.reason = self.rationale


class DecisionTrace(BaseModel):
    """
    Complete, explainable security decision trace.
    Exposes the factual chain of evidence from prompt to final verdict.
    """
    interception_id: str = Field(..., description="Unique tracking identifier for this interception event")
    timestamp: str = Field(default="", description="ISO 8601 timestamp of interception")
    final_decision: str = Field(..., description="Enforced verdict: ALLOW, REVIEW, or BLOCK")
    risk_score: float = Field(..., description="Normalized composite risk score (0.0 - 100.0)")
    risk_level: str = Field(..., description="Categorical risk tier: LOW, MEDIUM, HIGH, or CRITICAL")
    decision_confidence: DecisionConfidence = Field(default_factory=DecisionConfidence, description="Qualitative decision confidence assessment")
    short_explanation: str = Field(default="", description="Concise one-sentence decision summary")
    decision_reason: str = Field(default="", description="Brief reason for the decision")
    detailed_explanation: str = Field(default="", description="Comprehensive factual explanation of the decision")
    intent_analysis: Optional[IntentAnalysisTrace] = Field(default=None, description="Intent and consistency analysis trace")
    context_analysis: Optional[ContextAnalysisTrace] = Field(default=None, description="Operational context trace")
    behavior_analysis: Optional[BehaviorAnalysisTrace] = Field(default=None, description="Behavioral anomaly trace")
    resource_analysis: Optional[ResourceAnalysisTrace] = Field(default=None, description="Target resource sensitivity trace")
    risk_factors: List[RiskFactorContribution] = Field(default_factory=list, description="Active contributing risk factors")
    policy_analysis: Optional[PolicyAnalysisTrace] = Field(default=None, description="Security policies triggered and evaluated")
    reasoning_chain: List[ReasoningChainStep] = Field(default_factory=list, description="Visual step-by-step reasoning chain")
    safety_action: Optional[SafetyActionTrace] = Field(default=None, description="Containment boundary and safe simulation status")


class ExplainResponse(BaseModel):
    """Response payload for GET /explain/{interception_id}."""
    interception_id: str = Field(..., description="Unique interception identifier")
    decision_trace: DecisionTrace = Field(..., description="Comprehensive structured decision trace")
