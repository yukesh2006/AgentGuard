"""
AgentGuard Explainability API Router.
Phase 7: Endpoints for structured Explainable AI Decision Traces.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.decision_trace import ExplainResponse
from app.services.audit import get_audit_service
from app.services.explanation import get_explanation_engine

router = APIRouter(tags=["Explainability & Decision Traces"])


@router.get(
    "/explain/{interception_id}",
    response_model=ExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve complete Explainable AI Decision Trace for an interception event",
)
def get_decision_trace(interception_id: str) -> ExplainResponse:
    """
    Retrieve the end-to-end evidence chain, risk factor contributions,
    reasoning chain, and plain-English justification for a specific security interception event.
    """
    audit_service = get_audit_service()
    event = audit_service.get_event_by_id(interception_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event '{interception_id}' not found.",
        )

    explanation_engine = get_explanation_engine()
    trace = explanation_engine.build_trace_from_audit_event(event)

    return ExplainResponse(
        interception_id=event.interception_id,
        decision_trace=trace,
    )
