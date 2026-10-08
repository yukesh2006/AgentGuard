"""
AgentGuard Risk Assessment Engine.

Computes a multi-factor normalized risk score (0-100), categorical risk level,
behavioral anomaly status, and structured risk factor explanations.
"""

from typing import List, Dict, Any, Optional
from app.core.config import settings
from ml.intent.action_normalizer import normalize_action
from ml.intent.analyzer import get_intent_analyzer
from ml.intent.consistency import get_consistency_analyzer
from ml.context.engine import get_context_engine
from ml.anomaly.detector import get_anomaly_detector
from ml.risk.resource_classifier import classify_resource
from app.services.signals import evaluate_security_signals


class RiskAssessmentEngine:
    """
    Evaluates multi-factor risk combining semantic consistency, behavioral anomalies,
    resource sensitivity, action characteristics, and permissions.
    """

    def __init__(self) -> None:
        self.intent_analyzer = get_intent_analyzer()
        self.consistency_analyzer = get_consistency_analyzer()
        self.context_engine = get_context_engine()
        self.anomaly_detector = get_anomaly_detector()

    def assess_risk(
        self,
        user_request: str,
        agent_action: str,
        target_resource: str,
        previous_actions: Optional[List[str]] = None,
        user_permissions: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute full multi-factor risk assessment.
        """
        history = previous_actions if previous_actions is not None else []
        permissions = user_permissions if user_permissions is not None else ["standard_user"]

        # 1. Action Normalization
        action_dict = normalize_action(agent_action)

        # 2. Intent Analysis
        intent_dict = self.intent_analyzer.analyze(user_request)

        # 3. Context Processing
        context_dict = self.context_engine.process_context(
            goal=intent_dict["goal"],
            target_resource=target_resource,
            agent_action=action_dict["name"],
            explicit_resource_type=resource_type,
            session_id=session_id,
            user_id=user_id,
            previous_actions=history,
            user_permissions=permissions,
        )

        # 4. Intent-Action Consistency
        consistency_dict = self.consistency_analyzer.evaluate_consistency(
            user_request=user_request,
            action_description=action_dict["description"],
            target_resource=target_resource,
        )

        # 5. Security Signals Generation (Phase 2 integration)
        signals = evaluate_security_signals(
            user_request=user_request,
            intent_info=intent_dict,
            context_info=context_dict,
            action_info=action_dict,
            consistency_info=consistency_dict,
        )

        # 6. Behavioral Anomaly Detection (IsolationForest)
        behavior_result = self.anomaly_detector.detect_anomaly(
            previous_actions=history,
            current_action=action_dict["name"],
        )

        # 7. Resource Classification
        resource_info = classify_resource(target_resource)

        # 8. Multi-Factor Risk Calculation & Factor Explanations
        factors: List[Dict[str, Any]] = []
        raw_score = 0.0

        # Factor A: Intent-Action Consistency
        compatibility = consistency_dict.get("compatibility", "low")
        if compatibility == "low":
            impact = settings.weight_intent_inconsistency
            factors.append({
                "factor": "intent_action_consistency",
                "impact": impact,
                "reason": (
                    f"Action '{action_dict['name']}' has low semantic compatibility "
                    f"({consistency_dict['similarity_score']}) with the user's goal."
                ),
            })
            raw_score += impact
        elif compatibility == "medium":
            impact = round(settings.weight_intent_inconsistency * 0.4, 1)
            factors.append({
                "factor": "intent_action_consistency",
                "impact": impact,
                "reason": (
                    f"Action '{action_dict['name']}' exhibits moderate semantic compatibility "
                    f"({consistency_dict['similarity_score']}) with the user's goal."
                ),
            })
            raw_score += impact
        else:
            factors.append({
                "factor": "intent_action_consistency",
                "impact": 0.0,
                "reason": "The action is semantically consistent with the user's goal.",
            })

        # Factor B: Behavioral Anomaly
        if behavior_result["is_anomaly"]:
            b_severity = behavior_result["severity"]
            if b_severity == "high":
                impact = settings.weight_behavioral_anomaly
            else:
                impact = round(settings.weight_behavioral_anomaly * 0.6, 1)
            factors.append({
                "factor": "behavioral_anomaly",
                "impact": impact,
                "reason": (
                    f"Action sequence represents a behavioral anomaly compared to normal baseline "
                    f"(score: {behavior_result['anomaly_score']}, severity: {b_severity})."
                ),
            })
            raw_score += impact
        else:
            factors.append({
                "factor": "behavioral_anomaly",
                "impact": 0.0,
                "reason": (
                    f"Action sequence aligns with normal baseline behavior "
                    f"(score: {behavior_result['anomaly_score']})."
                ),
            })

        # Factor C: Destructive Action (from signals)
        destructive_signal = next(
            (s for s in signals if s["type"] == "destructive_action_anomaly"), None
        )
        if destructive_signal:
            impact = settings.weight_destructive_action
            factors.append({
                "factor": "destructive_action",
                "impact": impact,
                "reason": destructive_signal["description"],
            })
            raw_score += impact

        # Factor D: External Data Transfer (from signals)
        external_signal = next(
            (s for s in signals if s["type"] == "external_data_transfer"), None
        )
        if external_signal:
            impact = settings.weight_external_transfer
            factors.append({
                "factor": "external_data_transfer",
                "impact": impact,
                "reason": external_signal["description"],
            })
            raw_score += impact

        # Factor E: Unrelated System Command Execution (from signals)
        system_signal = next(
            (s for s in signals if s["type"] == "unrelated_system_execution"), None
        )
        if system_signal:
            impact = settings.weight_system_execution
            factors.append({
                "factor": "system_command_execution",
                "impact": impact,
                "reason": system_signal["description"],
            })
            raw_score += impact

        # Factor F: Resource Sensitivity
        if resource_info["is_sensitive"]:
            impact = settings.weight_resource_sensitivity
            factors.append({
                "factor": "resource_sensitivity",
                "impact": impact,
                "reason": (
                    f"Target resource '{target_resource}' is categorized as "
                    f"'{resource_info['category']}': {resource_info['description']}"
                ),
            })
            raw_score += impact

        # Factor G: Permission Context
        is_admin = any(p in ("admin", "superuser") for p in permissions)
        if action_dict["name"] in ("execute_command", "modify_permissions") and not is_admin:
            impact = settings.weight_permission_mismatch
            factors.append({
                "factor": "permission_context",
                "impact": impact,
                "reason": (
                    f"User permissions {permissions} are insufficient for privileged action "
                    f"'{action_dict['name']}' without administrative delegation."
                ),
            })
            raw_score += impact

        # 9. Score Normalization (0.0 to 100.0)
        final_score = round(max(0.0, min(100.0, raw_score)), 1)

        # 10. Risk Level Categorization
        if final_score < settings.risk_level_low_threshold:
            risk_level = "LOW"
        elif final_score < settings.risk_level_medium_threshold:
            risk_level = "MEDIUM"
        elif final_score < settings.risk_level_high_threshold:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        # 11. Human-Readable Explanation Synthesis
        active_factors = [f for f in factors if f["impact"] > 0]
        if not active_factors:
            explanation = (
                "The proposed action is consistent with the user's goal and does not show "
                "significant abnormal behavior."
            )
        else:
            reasons_summary = "; ".join(f["reason"] for f in active_factors[:3])
            explanation = (
                f"Risk evaluated as {risk_level} (score: {final_score}/100) due to: {reasons_summary}"
            )

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "behavior": behavior_result,
            "factors": factors,
            "explanation": explanation,
            "signals": signals,
            "consistency": consistency_dict,
            "action": action_dict,
            "intent": intent_dict,
            "context": context_dict,
            "resource": resource_info,
        }



# Global singleton instance
_risk_engine = None


def get_risk_engine() -> RiskAssessmentEngine:
    """Singleton getter for RiskAssessmentEngine."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskAssessmentEngine()
    return _risk_engine
