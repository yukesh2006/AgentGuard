"""
AgentGuard Agent Interception Orchestrator.

Intercepts proposed actions from autonomous AI agents, routes them through
semantic analysis, risk assessment, and policy decision evaluation, and coordinates
safe sandboxed simulation.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, Any

from app.models.interception import (
    InterceptionRequest,
    InterceptionResponse,
    ReviewStatusEnum,
)
from policy.schemas import PolicyDecisionRequest
from policy.engine import get_policy_engine
from app.services.simulator import SafeActionSimulator


class AgentInterceptor:
    """
    Gateway proxy intercepting proposed agent tool actions before execution.
    """

    def __init__(self) -> None:
        self.policy_engine = get_policy_engine()
        self.simulator = SafeActionSimulator()

    def intercept(self, payload: InterceptionRequest) -> InterceptionResponse:
        """
        Intercept proposed action, evaluate security policies, and determine
        whether to simulate, wait for review, or block.
        """
        # 1. Translate into policy evaluation request
        policy_req = PolicyDecisionRequest(
            user_request=payload.user_request,
            agent_action=payload.agent_action,
            target_resource=payload.target_resource,
            destination=payload.destination,
            previous_actions=payload.previous_actions,
            user_permissions=payload.user_permissions,
            session_id=payload.session_id,
            user_id=payload.user_id,
            resource_type=payload.resource_type,
        )

        # 2. Evaluate through the hierarchical policy engine with full intelligence context
        policy_res, risk_result = self.policy_engine.evaluate_request_with_context(policy_req)

        # 3. Coordinate safe simulation based on policy verdict
        sim_result = self.simulator.simulate(
            decision=policy_res.decision.value,
            action=policy_res.action or payload.agent_action,
            target_resource=policy_res.target_resource or payload.target_resource,
            user_request=payload.user_request,
        )

        # 4. Generate audit-ready interception metadata
        interception_id = f"AG-2026-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        review_status = (
            ReviewStatusEnum.PENDING
            if policy_res.decision.value == "REVIEW"
            else ReviewStatusEnum.NOT_REQUIRED
        )

        anomaly_detected = bool(risk_result.get("behavior", {}).get("is_anomaly", False))
        intent_similarity = risk_result.get("consistency", {}).get("similarity_score")

        # 5. Automatically persist audit event to SQLite database
        try:
            from app.services.audit import get_audit_service
            get_audit_service().log_interception(
                interception_id=interception_id,
                timestamp=timestamp,
                user_goal=payload.user_request or "",
                action=policy_res.action or payload.agent_action or "",
                target_resource=policy_res.target_resource or payload.target_resource or "",
                destination=payload.destination,
                decision=policy_res.decision.value,
                risk_score=policy_res.risk_score,
                risk_level=policy_res.risk_level,
                explanation=policy_res.reason,
                triggered_policies=policy_res.triggered_policies,
                simulation_status=(
                    sim_result["simulation_status"].value
                    if hasattr(sim_result["simulation_status"], "value")
                    else str(sim_result["simulation_status"])
                ),
                execution_permitted=sim_result["execution_permitted"],
                review_status=review_status.value,
                anomaly_detected=anomaly_detected,
                intent_similarity=intent_similarity,
                simulation_output=sim_result.get("simulation_output"),
            )
        except Exception:
            # Audit logging error should not break interception response in demo/edge environments
            pass

        return InterceptionResponse(
            interception_id=interception_id,
            timestamp=timestamp,
            decision=policy_res.decision.value,
            risk_score=policy_res.risk_score,
            risk_level=policy_res.risk_level,
            requires_human_review=policy_res.requires_human_review,
            action=policy_res.action or payload.agent_action,
            target_resource=policy_res.target_resource or payload.target_resource,
            destination=payload.destination,
            simulation_status=sim_result["simulation_status"],
            execution_permitted=sim_result["execution_permitted"],
            message=sim_result["message"],
            triggered_policies=policy_res.triggered_policies,
            reason=policy_res.reason,
            recommendation=policy_res.recommendation,
            review_status=review_status,
            anomaly_detected=anomaly_detected,
            simulation_output=sim_result.get("simulation_output"),
        )


# Global singleton instance
_interceptor = None


def get_agent_interceptor() -> AgentInterceptor:
    """Singleton getter for AgentInterceptor."""
    global _interceptor
    if _interceptor is None:
        _interceptor = AgentInterceptor()
    return _interceptor
