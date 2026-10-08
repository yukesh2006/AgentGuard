"""
AgentGuard Policy Rules Definition.

Defines deterministic, context-aware security rules that evaluate
intent, action characteristics, resource sensitivity, behavioral anomalies,
and risk assessments to produce enforceable verdicts: ALLOW, REVIEW, or BLOCK.
"""

from typing import Dict, Any, List, Optional, Tuple
from policy.schemas import DecisionEnum, PolicyIdentifier


class PolicyEvaluationResult:
    """Internal container for the result of a policy evaluation."""
    def __init__(
        self,
        decision: DecisionEnum,
        triggered_policies: List[str],
        reason: str,
        recommendation: str,
        requires_human_review: bool,
    ) -> None:
        self.decision = decision
        self.triggered_policies = triggered_policies
        self.reason = reason
        self.recommendation = recommendation
        self.requires_human_review = requires_human_review


# =====================================================================
# Hard Security Rules (BLOCK Criteria)
# =====================================================================

def evaluate_critical_risk_rule(context: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
    """
    Rule A: Critical Risk
    If aggregated risk is CRITICAL (score >= 75), block immediately.
    """
    risk_level = context.get("risk_level", "LOW")
    risk_score = context.get("risk_score", 0.0)

    if risk_level == "CRITICAL" or risk_score >= 75.0:
        triggered = [PolicyIdentifier.CRITICAL_RISK_BLOCK.value]
        # Include specific contributing policy flags
        if context.get("action", {}).get("name") == "execute_command":
            triggered.append(PolicyIdentifier.SYSTEM_COMMAND_RESTRICTION.value)
        if context.get("behavior", {}).get("is_anomaly"):
            triggered.append(PolicyIdentifier.BEHAVIORAL_ANOMALY.value)

        return PolicyEvaluationResult(
            decision=DecisionEnum.BLOCK,
            triggered_policies=triggered,
            reason=(
                f"The proposed action presents critical security risk (score: {risk_score}/100) "
                f"with severe compounding threat signals."
            ),
            recommendation="Terminate execution immediately and log security incident.",
            requires_human_review=False,
        )
    return None


def evaluate_sensitive_external_transfer_rule(context: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
    """
    Rule B: Sensitive External Transfer
    If action is external transfer/upload without user authorization, or targeting an untrusted endpoint.
    """
    action_name = context.get("action", {}).get("name", "")
    target_resource = context.get("target_resource", "")
    resource_info = context.get("resource", {})
    signals = context.get("signals", [])
    user_request = context.get("user_request", "").lower()

    is_upload = action_name == "upload_external" or "upload" in action_name
    is_external_target = (
        resource_info.get("category") == "external_destination"
        or "unknown" in target_resource.lower()
        or target_resource.startswith(("http://", "https://"))
    )

    external_signal = any(s.get("type") == "external_data_transfer" for s in signals)
    user_authorized = any(kw in user_request for kw in ("upload", "publish", "share to external", "send externally"))

    if (is_upload or is_external_target) and (external_signal or not user_authorized):
        triggered = [PolicyIdentifier.SENSITIVE_EXTERNAL_TRANSFER.value]
        if context.get("consistency", {}).get("compatibility") == "low":
            triggered.append(PolicyIdentifier.INTENT_ACTION_MISMATCH.value)

        return PolicyEvaluationResult(
            decision=DecisionEnum.BLOCK,
            triggered_policies=triggered,
            reason=(
                "The requested action attempts to transfer project data to an external destination "
                "that is not related to or justified by the user's stated goal."
            ),
            recommendation="Block the external transfer and require explicit administrative clearance.",
            requires_human_review=False,
        )
    return None


def evaluate_system_command_rule(context: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
    """
    Rule E: Dangerous System-Level Action
    If action is a system/shell command and intent does not clearly request administrative work.
    """
    action_name = context.get("action", {}).get("name", "")
    user_request = context.get("user_request", "").lower()
    intent_category = context.get("intent", {}).get("intent", "")

    if action_name == "execute_command":
        admin_keywords = ("run command", "terminal", "bash", "execute shell", "system admin", "cli")
        is_admin_intent = intent_category == "system_administration" or any(kw in user_request for kw in admin_keywords)

        if not is_admin_intent:
            triggered = [PolicyIdentifier.SYSTEM_COMMAND_RESTRICTION.value]
            if context.get("consistency", {}).get("compatibility") == "low":
                triggered.append(PolicyIdentifier.INTENT_ACTION_MISMATCH.value)
            if context.get("behavior", {}).get("is_anomaly"):
                triggered.append(PolicyIdentifier.BEHAVIORAL_ANOMALY.value)

            return PolicyEvaluationResult(
                decision=DecisionEnum.BLOCK,
                triggered_policies=triggered,
                reason=(
                    "The agent attempted system command execution without corresponding administrative "
                    "intent in the user's goal."
                ),
                recommendation="Block execution and inspect agent reasoning trace for possible prompt injection.",
                requires_human_review=False,
            )
    return None


def evaluate_intent_mismatch_destructive_rule(context: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
    """
    Rule C: Strong Intent-Action Mismatch on Destructive Operations
    If action is destructive and intent consistency is low or task does not justify deletion.
    """
    action_name = context.get("action", {}).get("name", "")
    user_request = context.get("user_request", "").lower()
    consistency = context.get("consistency", {})
    compatibility = consistency.get("compatibility", "low")

    is_destructive = action_name == "delete_project_file" or "delete" in action_name
    deletion_keywords = ("delete", "remove", "clean", "purge", "erase")
    asks_deletion = any(kw in user_request for kw in deletion_keywords)

    if is_destructive:
        if not asks_deletion:
            # Unrequested deletion during a non-destructive task (e.g. "Prepare report") -> BLOCK
            return PolicyEvaluationResult(
                decision=DecisionEnum.BLOCK,
                triggered_policies=[
                    PolicyIdentifier.DESTRUCTIVE_ACTION.value,
                    PolicyIdentifier.INTENT_ACTION_MISMATCH.value,
                ],
                reason=(
                    "The requested action is destructive ('delete_project_file'), while the user's goal "
                    "is non-destructive. This indicates an intent-action mismatch."
                ),
                recommendation="Block file deletion and require user re-confirmation.",
                requires_human_review=False,
            )
        else:
            # User asked to clean up or delete, but it's destructive -> REVIEW for confirmation
            return PolicyEvaluationResult(
                decision=DecisionEnum.REVIEW,
                triggered_policies=[PolicyIdentifier.DESTRUCTIVE_ACTION.value],
                reason=(
                    "The action is potentially destructive. The user's request may justify deletion, "
                    "but explicit confirmation is recommended before removing project data."
                ),
                recommendation="Require explicit human confirmation before deleting project resources.",
                requires_human_review=True,
            )
    return None


# =====================================================================
# Human Review Rules (REVIEW Criteria)
# =====================================================================

def evaluate_sensitive_resource_access_rule(context: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
    """
    Rule D: Sensitive Resource Access
    If resource contains credentials, passwords, or keys, and user intent does not explicitly justify it.
    """
    resource_info = context.get("resource", {})
    target_resource = context.get("target_resource", "")
    user_request = context.get("user_request", "").lower()

    if resource_info.get("category") == "sensitive_credentials" or resource_info.get("is_sensitive"):
        cred_keywords = ("credential", "password", "secret", "private key", "auth token")
        explicit_cred_intent = any(kw in user_request for kw in cred_keywords)

        if not explicit_cred_intent:
            return PolicyEvaluationResult(
                decision=DecisionEnum.REVIEW,
                triggered_policies=[PolicyIdentifier.SENSITIVE_RESOURCE_ACCESS.value],
                reason=(
                    f"The requested resource '{target_resource}' contains sensitive credentials, "
                    f"and the user's stated goal does not clearly justify access."
                ),
                recommendation="Require human supervisor authorization before reading sensitive credentials.",
                requires_human_review=True,
            )
    return None


def evaluate_moderate_risk_review_rule(context: Dict[str, Any]) -> Optional[PolicyEvaluationResult]:
    """
    Evaluates moderate risk levels (MEDIUM or ambiguous HIGH) where no hard block rule was triggered.
    """
    risk_level = context.get("risk_level", "LOW")
    risk_score = context.get("risk_score", 0.0)

    if risk_level == "HIGH":
        return PolicyEvaluationResult(
            decision=DecisionEnum.REVIEW,
            triggered_policies=[PolicyIdentifier.HIGH_RISK_REVIEW.value],
            reason=(
                f"Elevated risk score ({risk_score}/100) indicates contextual ambiguity "
                f"warranting human confirmation."
            ),
            recommendation="Place action in review queue for human-in-the-loop validation.",
            requires_human_review=True,
        )
    elif risk_level == "MEDIUM":
        return PolicyEvaluationResult(
            decision=DecisionEnum.REVIEW,
            triggered_policies=[PolicyIdentifier.MEDIUM_RISK_REVIEW.value],
            reason=(
                f"Moderate risk score ({risk_score}/100) detected. Action requires human review "
                f"prior to execution."
            ),
            recommendation="Review the proposed operation before granting authorization.",
            requires_human_review=True,
        )
    return None


# =====================================================================
# Safe Allow Rule (ALLOW Criteria)
# =====================================================================

def evaluate_safe_allow_rule(context: Dict[str, Any]) -> PolicyEvaluationResult:
    """
    Evaluates benign, aligned, low-risk actions for automatic pass-through.
    """
    action_name = context.get("action", {}).get("name", "")
    user_request = context.get("user_request", "")

    if action_name == "send_email":
        reason = "The requested email action directly supports the user's stated communication goal and presents low risk."
    else:
        reason = (
            f"The requested '{action_name}' operation is consistent with the user's stated goal "
            f"and presents low security risk."
        )

    return PolicyEvaluationResult(
        decision=DecisionEnum.ALLOW,
        triggered_policies=[PolicyIdentifier.LOW_RISK_ALIGNED_ACTION.value],
        reason=reason,
        recommendation="Allow action execution through the security gateway.",
        requires_human_review=False,
    )
