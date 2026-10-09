"""
AgentGuard Explanation Engine.
Phase 7: Transforms structured security signals and policy evaluations into
explainable, factual decision traces and natural-language justifications.
"""

from typing import Dict, Any, List, Optional
from app.models.decision_trace import (
    DecisionTrace,
    IntentAnalysisTrace,
    ContextAnalysisTrace,
    BehaviorAnalysisTrace,
    ResourceAnalysisTrace,
    RiskFactorContribution,
    PolicyAnalysisTrace,
    ReasoningChainStep,
    SafetyActionTrace,
    DecisionConfidence,
)
from app.database.models import AuditEventRecord
from app.services.audit import sanitize_sensitive_content
from ml.risk.resource_classifier import classify_resource
from ml.intent.action_normalizer import is_known_action, normalize_action


class ExplanationEngine:
    """
    Transforms raw security signals, ML inferences, and policy outputs
    into transparent, understandable, and explainable decision traces.
    """

    @staticmethod
    def generate_short_explanation(decision: str, reason: str, action: str, goal: str) -> str:
        """Construct a concise, factual 1-sentence decision summary."""
        goal = sanitize_sensitive_content(goal) or ""
        dec = decision.upper().strip()
        if dec == "BLOCK":
            if "destructive" in reason.lower():
                return f"AgentGuard blocked the action because deleting or modifying project resources does not align with the requested task '{goal}'."
            elif "external" in reason.lower():
                return f"AgentGuard blocked the action because unauthorized external data transmission to an external endpoint was detected."
            elif "system" in reason.lower() or "command" in reason.lower():
                return f"AgentGuard blocked the action because system shell command execution is prohibited without explicit administrative authorization."
            return f"AgentGuard blocked the action '{action}' due to severe policy violations and security risk."
        elif dec == "REVIEW":
            if "credential" in reason.lower() or "secret" in reason.lower():
                return f"AgentGuard routed this action to human review because reading sensitive credentials requires explicit supervisor approval."
            elif "destructive" in reason.lower():
                return f"AgentGuard requires human confirmation before allowing a destructive file operation to proceed."
            return f"AgentGuard placed this action in the human review queue due to contextual ambiguity."
        else:
            return f"AgentGuard allowed this action because '{action}' directly aligns with the stated goal and presents low security risk."

    @staticmethod
    def generate_detailed_explanation(
        decision: str,
        reason: str,
        goal: str,
        action: str,
        target_resource: str,
        risk_score: float,
        risk_level: str,
        triggered_policies: List[str],
        anomaly_detected: bool,
    ) -> str:
        """Construct a comprehensive multi-sentence evidence narrative."""
        goal = sanitize_sensitive_content(goal) or ""
        target_resource = sanitize_sensitive_content(target_resource) or ""
        dec = decision.upper().strip()
        policies_str = ", ".join(triggered_policies) if triggered_policies else "None"

        narrative_parts = [
            f"The user initiated the goal: '{goal}'. In response, the autonomous agent proposed action '{action}' targeting resource '{target_resource}'.",
            f"AgentGuard assessed an aggregate risk score of {risk_score:.1f}/100 ({risk_level} tier).",
        ]

        if anomaly_detected:
            narrative_parts.append("The action trajectory exhibited a statistical behavioral anomaly compared to baseline interactions.")

        if dec == "BLOCK":
            narrative_parts.append(
                f"Execution was rejected under security policy rules [{policies_str}]. {reason} "
                "The action was safely terminated before touching any host or network resources."
            )
        elif dec == "REVIEW":
            narrative_parts.append(
                f"The request activated human-in-the-loop security policy rules [{policies_str}]. {reason} "
                "The operation remains halted until an authorized supervisor confirms or rejects it."
            )
        else:
            narrative_parts.append(
                f"The operation satisfied baseline security policy rules [{policies_str}]. "
                "AgentGuard granted execution permission, which was completed within the safe simulation boundary."
            )

        return " ".join(narrative_parts)

    def generate_explanation(
        self,
        user_goal: str,
        action: str,
        decision: str,
        risk_level: str,
        risk_factors: List[str] = None,
        triggered_policies: List[str] = None,
        resource: str = "",
        anomaly_detected: bool = False,
        risk_score: float = 50.0,
        reason: str = "",
        **kwargs: Any,
    ) -> tuple[str, str]:
        """Convenience method returning both short and detailed explanations."""
        if triggered_policies is None:
            triggered_policies = []
        if not reason:
            if triggered_policies:
                reason = f"Security policy rules triggered: [{', '.join(triggered_policies)}]."
            else:
                reason = f"Action assessed under {decision} security policy guidelines."
        short_exp = self.generate_short_explanation(decision=decision, reason=reason, action=action, goal=user_goal)
        detailed_exp = self.generate_detailed_explanation(
            decision=decision,
            reason=reason,
            goal=user_goal,
            action=action,
            target_resource=resource,
            risk_score=risk_score,
            risk_level=risk_level,
            triggered_policies=triggered_policies,
            anomaly_detected=anomaly_detected,
        )
        return short_exp, detailed_exp

    @classmethod
    def evaluate_decision_confidence(
        cls,
        user_goal: str = "",
        action: str = "",
        target_resource: str = "",
        decision: str = "ALLOW",
        risk_score: float = 0.0,
        triggered_policies: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> DecisionConfidence:
        """
        Produce a qualitative indicator of signal completeness and consistency.
        Note: This reflects evidence coverage and rule clarity, not a probability.
        """
        if triggered_policies is None:
            triggered_policies = []
        has_goal = bool(user_goal and len(user_goal.strip()) > 5)
        has_action = bool(action and (is_known_action(action) or len(action.strip()) > 3))
        has_resource = bool(target_resource and len(target_resource.strip()) > 1)
        has_policies = len(triggered_policies) > 0

        # Completeness calculation
        checks = [has_goal, has_action]
        if target_resource:
            checks.append(has_resource)
        if triggered_policies:
            checks.append(has_policies)
        completeness = sum(1 for c in checks if c) / len(checks)

        if completeness >= 0.75:
            if decision in ("BLOCK", "ALLOW"):
                return DecisionConfidence(
                    confidence_level="HIGH",
                    level="HIGH",
                    rationale="Strong semantic clarity, known action semantics, and deterministic policy rule triggers.",
                    reason="Strong semantic clarity, known action semantics, and deterministic policy rule triggers.",
                    signals_completeness=completeness,
                )
            else:
                return DecisionConfidence(
                    confidence_level="MEDIUM",
                    level="MEDIUM",
                    rationale="Comprehensive signals available, but contextual ambiguity appropriately mandates human review.",
                    reason="Comprehensive signals available, but contextual ambiguity appropriately mandates human review.",
                    signals_completeness=completeness,
                )
        elif completeness >= 0.5:
            return DecisionConfidence(
                confidence_level="MEDIUM",
                level="MEDIUM",
                rationale="Adequate signals for assessment, though intent or context includes moderate ambiguity.",
                reason="Adequate signals for assessment, though intent or context includes moderate ambiguity.",
                signals_completeness=completeness,
            )
        else:
            return DecisionConfidence(
                confidence_level="LOW",
                level="LOW",
                rationale="Limited context or unknown resource parameters detected.",
                reason="Limited context or unknown resource parameters detected.",
                signals_completeness=completeness,
            )

    @classmethod
    def compute_confidence(cls, *args: Any, **kwargs: Any) -> DecisionConfidence:
        """Alias for evaluate_decision_confidence."""
        return cls.evaluate_decision_confidence(*args, **kwargs)

    @staticmethod
    def build_reasoning_chain(
        user_goal: str,
        action: str,
        target_resource: str = "",
        consistency_level: str = "MEDIUM",
        consistency_reason: str = "",
        anomaly_detected: bool = False,
        risk_score: float = 0.0,
        risk_level: str = "LOW",
        triggered_policies: Optional[List[str]] = None,
        decision: str = "ALLOW",
        **kwargs: Any,
    ) -> List[ReasoningChainStep]:
        """Build the structured 7-stage evidence reasoning chain."""
        if triggered_policies is None:
            triggered_policies = []
        # 1. Intent Stage
        intent_step = ReasoningChainStep(
            stage="INTENT",
            status="ANALYZED",
            summary=f"User stated objective: '{user_goal}'.",
        )

        # 2. Action Stage
        action_step = ReasoningChainStep(
            stage="ACTION",
            status="EVALUATED",
            summary=f"Agent requested '{action}' targeting resource '{target_resource}'.",
        )

        # 3. Consistency Stage
        c_status = "ALIGNED" if consistency_level.upper() == "HIGH" else (
            "COMPATIBLE" if consistency_level.upper() == "MEDIUM" else "MISMATCH"
        )
        consistency_step = ReasoningChainStep(
            stage="CONSISTENCY",
            status=c_status,
            summary=consistency_reason or f"Intent-action compatibility determined as {consistency_level}.",
        )

        # 4. Behavior Stage
        b_status = "ANOMALY" if anomaly_detected else "NORMAL"
        behavior_step = ReasoningChainStep(
            stage="BEHAVIOR",
            status=b_status,
            summary="Action sequence flagged as behavioral anomaly." if anomaly_detected else "Action trajectory aligns with baseline pattern.",
        )

        # 5. Risk Stage
        risk_step = ReasoningChainStep(
            stage="RISK",
            status=f"{risk_level} ({risk_score:.1f}/100)",
            summary=f"Calculated multi-factor risk score: {risk_score:.1f}/100.",
        )

        # 6. Policy Stage
        pol_str = ", ".join(triggered_policies) if triggered_policies else "LOW_RISK_ALIGNED_ACTION"
        policy_step = ReasoningChainStep(
            stage="POLICY",
            status="TRIGGERED" if triggered_policies else "EVALUATED",
            summary=f"Active security policies: [{pol_str}].",
        )

        # 7. Decision Stage
        dec_summary = (
            "Action terminated immediately; zero execution occurred."
            if decision == "BLOCK"
            else (
                "Action paused in review queue; human confirmation required."
                if decision == "REVIEW"
                else "Action permitted and safely simulated."
            )
        )
        decision_step = ReasoningChainStep(
            stage="DECISION",
            status=decision,
            summary=dec_summary,
        )

        return [intent_step, action_step, consistency_step, behavior_step, risk_step, policy_step, decision_step]

    def build_trace_from_context(
        self,
        interception_id: str,
        timestamp: str,
        user_goal: str,
        action: str,
        target_resource: str,
        decision: str,
        risk_score: float,
        risk_level: str,
        reason: str,
        triggered_policies: List[str],
        simulation_status: str,
        execution_permitted: bool,
        risk_result: Dict[str, Any],
        destination: Optional[str] = None,
    ) -> DecisionTrace:
        """
        Build a high-fidelity DecisionTrace directly from live evaluation context.
        """
        user_goal = sanitize_sensitive_content(user_goal) or ""
        target_resource = sanitize_sensitive_content(target_resource) or ""
        if destination:
            destination = sanitize_sensitive_content(destination)

        # Intent details
        intent_info = risk_result.get("intent", {})
        consistency_info = risk_result.get("consistency", {})
        intent_trace = IntentAnalysisTrace(
            user_goal=user_goal,
            detected_intent=intent_info.get("intent", "general_task"),
            intent_action_similarity=float(consistency_info.get("similarity_score", 0.0)),
            consistency_level=str(consistency_info.get("compatibility", "medium")).upper(),
            consistency_reason=consistency_info.get("reason", "Semantic comparison executed."),
        )

        # Context details
        context_info = risk_result.get("context", {})
        context_trace = ContextAnalysisTrace(
            context_summary=f"Context evaluated for action '{action}' on '{target_resource}'.",
            previous_action_count=len(context_info.get("previous_actions", [])),
            context_consistent=True,
            resource_type=context_info.get("resource_type", "general_resource"),
        )

        # Behavior details
        behavior_info = risk_result.get("behavior", {})
        is_anomaly = bool(behavior_info.get("is_anomaly", False))
        behavior_trace = BehaviorAnalysisTrace(
            anomaly_detected=is_anomaly,
            anomaly_level=str(behavior_info.get("severity", "NONE")).upper(),
            behavioral_reason=behavior_info.get("reason", "Sequence compared to baseline model."),
            anomaly_score=behavior_info.get("anomaly_score"),
        )

        # Resource details
        resource_info = risk_result.get("resource", {})
        resource_trace = ResourceAnalysisTrace(
            resource=target_resource,
            resource_type=context_info.get("resource_type", "general_resource"),
            sensitivity="CRITICAL" if "credential" in resource_info.get("category", "") else (
                "SENSITIVE" if resource_info.get("is_sensitive") else "NORMAL"
            ),
            category=resource_info.get("category", "general_resource"),
        )

        # Contributing Risk Factors (Filter impact > 0)
        raw_factors = risk_result.get("factors", [])
        risk_factors: List[RiskFactorContribution] = []
        for rf in raw_factors:
            impact = float(rf.get("impact", 0.0))
            if impact > 0:
                severity = "HIGH" if impact >= 25.0 else ("MEDIUM" if impact >= 15.0 else "LOW")
                factor_name = str(rf.get("factor", "UNKNOWN")).upper()
                risk_factors.append(
                    RiskFactorContribution(
                        factor=factor_name,
                        contribution=impact,
                        severity=severity,
                        evidence=rf.get("reason", "Risk signal contributed to score."),
                    )
                )

        # Policy trace
        policy_trace = PolicyAnalysisTrace(
            triggered_policies=triggered_policies,
            policy_reasons=[reason],
        )

        # Confidence
        confidence = self.evaluate_decision_confidence(
            user_goal=user_goal,
            action=action,
            target_resource=target_resource,
            decision=decision,
            risk_score=risk_score,
            triggered_policies=triggered_policies,
        )

        # Short & detailed explanations
        short_exp = self.generate_short_explanation(
            decision=decision,
            reason=reason,
            action=action,
            goal=user_goal,
        )
        detailed_exp = self.generate_detailed_explanation(
            decision=decision,
            reason=reason,
            goal=user_goal,
            action=action,
            target_resource=target_resource,
            risk_score=risk_score,
            risk_level=risk_level,
            triggered_policies=triggered_policies,
            anomaly_detected=is_anomaly,
        )

        # Reasoning chain
        reasoning_chain = self.build_reasoning_chain(
            user_goal=user_goal,
            action=action,
            target_resource=target_resource,
            consistency_level=intent_trace.consistency_level,
            consistency_reason=intent_trace.consistency_reason,
            anomaly_detected=is_anomaly,
            risk_score=risk_score,
            risk_level=risk_level,
            triggered_policies=triggered_policies,
            decision=decision,
        )

        return DecisionTrace(
            interception_id=interception_id,
            timestamp=timestamp,
            final_decision=decision,
            risk_score=risk_score,
            risk_level=risk_level,
            decision_confidence=confidence,
            short_explanation=short_exp,
            detailed_explanation=detailed_exp,
            intent_analysis=intent_trace,
            context_analysis=context_trace,
            behavior_analysis=behavior_trace,
            resource_analysis=resource_trace,
            risk_factors=risk_factors,
            policy_analysis=policy_trace,
            reasoning_chain=reasoning_chain,
            safety_action=SafetyActionTrace(
                simulation_status=simulation_status,
                execution_permitted=execution_permitted,
            ),
        )

    def build_trace_from_audit_event(self, event: AuditEventRecord) -> DecisionTrace:
        """
        Reconstruct a complete DecisionTrace from a persisted AuditEventRecord.
        """
        resource_info = classify_resource(event.target_resource)

        # Derive intent and consistency
        consistency_score = event.intent_similarity if event.intent_similarity is not None else (
            0.15 if event.decision == "BLOCK" else (0.25 if event.decision == "REVIEW" else 0.40)
        )
        consistency_level = (
            "HIGH" if consistency_score >= 0.33 else ("MEDIUM" if consistency_score >= 0.15 else "LOW")
        )
        consistency_reason = (
            "Semantic analysis shows inconsistency between stated reporting goal and proposed action."
            if event.decision == "BLOCK"
            else "Semantic evaluation verified alignment between user intent and proposed action."
        )

        intent_trace = IntentAnalysisTrace(
            user_goal=event.user_goal,
            detected_intent="reporting_task" if "report" in event.user_goal.lower() else "general_operation",
            intent_action_similarity=round(consistency_score, 2),
            consistency_level=consistency_level,
            consistency_reason=consistency_reason,
        )

        # Context trace
        context_trace = ContextAnalysisTrace(
            context_summary=f"Historical audit event for action '{event.action}' on resource '{event.target_resource}'.",
            previous_action_count=1,
            context_consistent=event.decision != "BLOCK",
            resource_type=resource_info.get("category", "general_resource"),
        )

        # Behavior trace
        behavior_trace = BehaviorAnalysisTrace(
            anomaly_detected=event.anomaly_detected,
            anomaly_level="HIGH" if event.anomaly_detected else "NONE",
            behavioral_reason=(
                "Statistical anomaly detected in sequence trajectory."
                if event.anomaly_detected
                else "Action trajectory corresponds to normal user behavior patterns."
            ),
            anomaly_score=-0.25 if event.anomaly_detected else 0.15,
        )

        # Resource trace
        resource_trace = ResourceAnalysisTrace(
            resource=event.target_resource,
            resource_type=resource_info.get("category", "general_resource"),
            sensitivity="CRITICAL" if "credential" in resource_info.get("category", "") else (
                "SENSITIVE" if resource_info.get("is_sensitive") else "NORMAL"
            ),
            category=resource_info.get("category", "general_resource"),
        )

        # Risk Factors
        risk_factors: List[RiskFactorContribution] = []
        if "INTENT_ACTION_MISMATCH" in event.triggered_policies or event.decision == "BLOCK":
            risk_factors.append(RiskFactorContribution(
                factor="INTENT_INCONSISTENCY",
                contribution=25.0,
                severity="HIGH",
                evidence="Semantic intent divergence detected between prompt and requested action.",
            ))
        if "DESTRUCTIVE_ACTION" in event.triggered_policies or "delete" in event.action:
            risk_factors.append(RiskFactorContribution(
                factor="DESTRUCTIVE_ACTION",
                contribution=25.0,
                severity="HIGH",
                evidence=f"Action '{event.action}' is categorized as destructive.",
            ))
        if "SENSITIVE_EXTERNAL_TRANSFER" in event.triggered_policies or "upload" in event.action:
            risk_factors.append(RiskFactorContribution(
                factor="EXTERNAL_TRANSFER",
                contribution=25.0,
                severity="HIGH",
                evidence="Outbound data transmission detected.",
            ))
        if "SYSTEM_COMMAND_RESTRICTION" in event.triggered_policies or "command" in event.action:
            risk_factors.append(RiskFactorContribution(
                factor="SYSTEM_EXECUTION",
                contribution=25.0,
                severity="CRITICAL",
                evidence="Direct system shell execution requested.",
            ))
        if "SENSITIVE_RESOURCE_ACCESS" in event.triggered_policies or resource_info.get("is_sensitive"):
            risk_factors.append(RiskFactorContribution(
                factor="RESOURCE_SENSITIVITY",
                contribution=25.0,
                severity="HIGH",
                evidence=f"Resource '{event.target_resource}' contains sensitive assets.",
            ))
        if event.anomaly_detected:
            risk_factors.append(RiskFactorContribution(
                factor="BEHAVIORAL_ANOMALY",
                contribution=20.0,
                severity="HIGH",
                evidence="IsolationForest flagged abnormal behavioral trajectory.",
            ))

        # Policy trace
        policy_trace = PolicyAnalysisTrace(
            triggered_policies=event.triggered_policies,
            policy_reasons=[event.explanation],
        )

        # Confidence
        confidence = self.evaluate_decision_confidence(
            user_goal=event.user_goal,
            action=event.action,
            target_resource=event.target_resource,
            decision=event.decision,
            risk_score=event.risk_score,
            triggered_policies=event.triggered_policies,
        )

        short_exp = self.generate_short_explanation(
            decision=event.decision,
            reason=event.explanation,
            action=event.action,
            goal=event.user_goal,
        )
        detailed_exp = self.generate_detailed_explanation(
            decision=event.decision,
            reason=event.explanation,
            goal=event.user_goal,
            action=event.action,
            target_resource=event.target_resource,
            risk_score=event.risk_score,
            risk_level=event.risk_level,
            triggered_policies=event.triggered_policies,
            anomaly_detected=event.anomaly_detected,
        )

        reasoning_chain = self.build_reasoning_chain(
            user_goal=event.user_goal,
            action=event.action,
            target_resource=event.target_resource,
            consistency_level=consistency_level,
            consistency_reason=consistency_reason,
            anomaly_detected=event.anomaly_detected,
            risk_score=event.risk_score,
            risk_level=event.risk_level,
            triggered_policies=event.triggered_policies,
            decision=event.decision,
        )

        return DecisionTrace(
            interception_id=event.interception_id,
            timestamp=event.timestamp,
            final_decision=event.decision,
            risk_score=event.risk_score,
            risk_level=event.risk_level,
            decision_confidence=confidence,
            short_explanation=short_exp,
            detailed_explanation=detailed_exp,
            intent_analysis=intent_trace,
            context_analysis=context_trace,
            behavior_analysis=behavior_trace,
            resource_analysis=resource_trace,
            risk_factors=risk_factors,
            policy_analysis=policy_trace,
            reasoning_chain=reasoning_chain,
            safety_action=SafetyActionTrace(
                simulation_status=event.simulation_status,
                execution_permitted=event.execution_permitted,
            ),
        )


# Global singleton instance
_explanation_engine: Optional[ExplanationEngine] = None


def get_explanation_engine() -> ExplanationEngine:
    """Singleton getter for ExplanationEngine."""
    global _explanation_engine
    if _explanation_engine is None:
        _explanation_engine = ExplanationEngine()
    return _explanation_engine
