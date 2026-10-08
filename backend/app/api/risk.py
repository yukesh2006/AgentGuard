"""
AgentGuard API Router: /risk-assessment Endpoint.

Evaluates multi-factor risk, behavioral anomalies, and operational context
for proposed AI agent operations.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    BehaviorResult,
    RiskFactor,
    SecuritySignal,
    ConsistencyResult,
    ActionInfo,
)
from ml.risk.engine import get_risk_engine

router = APIRouter(tags=["Risk Assessment"])


@router.post(
    "/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate multi-factor risk for proposed agent action",
)
def assess_action_risk(payload: RiskAssessmentRequest) -> RiskAssessmentResponse:
    """
    Evaluates multi-dimensional risk for an AI agent's proposed action,
    analyzing semantic intent consistency, behavioral sequence anomalies,
    resource sensitivity, and authorization context.
    """
    engine = get_risk_engine()

    try:
        result = engine.assess_risk(
            user_request=payload.user_request,
            agent_action=payload.agent_action,
            target_resource=payload.target_resource,
            previous_actions=payload.previous_actions,
            user_permissions=payload.user_permissions,
            session_id=payload.session_id,
            user_id=payload.user_id,
            resource_type=payload.resource_type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment engine error: {exc}",
        ) from exc

    return RiskAssessmentResponse(
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        behavior=BehaviorResult(**result["behavior"]),
        factors=[RiskFactor(**f) for f in result["factors"]],
        explanation=result["explanation"],
        signals=[SecuritySignal(**s) for s in result.get("signals", [])],
        consistency=ConsistencyResult(**result["consistency"]) if result.get("consistency") else None,
        action=ActionInfo(**result["action"]) if result.get("action") else None,
    )
