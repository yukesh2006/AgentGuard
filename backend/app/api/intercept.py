"""
AgentGuard API Router: /intercept and /agent/intercept Endpoints.

Phase 5: Agent Interception Layer & Safe Action Simulation.
Intercepts AI agent tool action proposals, validates against security policies,
and returns safe sandboxed simulation results.
"""

from fastapi import APIRouter, HTTPException, Query, status
from app.models.interception import InterceptionRequest, InterceptionResponse
from app.services.interceptor import get_agent_interceptor

router = APIRouter(tags=["Agent Interception"])


@router.post(
    "/intercept",
    response_model=InterceptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Intercept and safely simulate an AI agent proposed action",
)
@router.post(
    "/agent/intercept",
    response_model=InterceptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Alias for /intercept",
    include_in_schema=False,
)
def intercept_agent_action(
    payload: InterceptionRequest,
    include_trace: bool = Query(default=False, description="Optionally include Phase 7 Explainable AI Decision Trace"),
) -> InterceptionResponse:
    """
    Intercept an action proposed by an autonomous AI agent, evaluate it
    against AgentGuard's intent-action consistency, behavioral anomaly detection,
    risk assessment, and security policy rules, and safely simulate the outcome.

    Under NO circumstances will real dangerous actions (file deletions, system
    commands, credential extraction, or external exfiltration) be executed.
    """
    interceptor = get_agent_interceptor()

    try:
        return interceptor.intercept(payload, include_trace=include_trace)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent interception pipeline error: {exc}",
        ) from exc
