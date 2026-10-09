"""
AgentGuard Security Intelligence API Router.
Phase 7: Endpoints for threat intelligence aggregation and active pattern detection.
"""

from fastapi import APIRouter, status
from app.services.intelligence import (
    get_security_intelligence_service,
    SecurityIntelligenceResponse,
)

router = APIRouter(prefix="/security", tags=["Security Intelligence & Threat Patterns"])


@router.get(
    "/intelligence",
    response_model=SecurityIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve enterprise security intelligence, threat patterns, and policy rankings",
)
def get_security_intelligence() -> SecurityIntelligenceResponse:
    """
    Returns aggregated threat intelligence, most frequent blocked actions,
    active multi-event threat patterns, and risk/decision distributions.
    """
    service = get_security_intelligence_service()
    return service.get_security_intelligence()
