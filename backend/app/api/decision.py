"""
AgentGuard API Router: /policy-decision and /decision Endpoints.

Evaluates incoming agent action proposals against security policies to produce
final enforceable verdicts: ALLOW, REVIEW, or BLOCK.
"""

from fastapi import APIRouter, HTTPException, status
from policy.schemas import PolicyDecisionRequest, PolicyDecisionResponse
from policy.engine import get_policy_engine

router = APIRouter(tags=["Policy Decision"])


@router.post(
    "/policy-decision",
    response_model=PolicyDecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate context-aware policy decision (ALLOW, REVIEW, BLOCK)",
)
@router.post(
    "/decision",
    response_model=PolicyDecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Alias for /policy-decision",
    include_in_schema=False,
)
def evaluate_policy_decision(payload: PolicyDecisionRequest) -> PolicyDecisionResponse:
    """
    Evaluates whether an AI agent's proposed action should be ALLOWED,
    sent for human REVIEW, or BLOCKED, based on multi-factor context,
    intent alignment, behavioral trajectory, and security policies.
    """
    engine = get_policy_engine()

    try:
        return engine.evaluate_request(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Policy decision engine error: {exc}",
        ) from exc
