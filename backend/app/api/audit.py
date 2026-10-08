"""
AgentGuard Audit API Router.
Phase 6: Endpoints for audit event logs, stats, and policy trigger analytics.
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, status
from app.database.models import AuditEventRecord, AuditStatsResponse
from app.services.audit import get_audit_service

router = APIRouter(prefix="/audit", tags=["Audit & Security Dashboard"])


@router.get(
    "/events",
    response_model=List[AuditEventRecord],
    status_code=status.HTTP_200_OK,
    summary="Retrieve persistent security audit events with optional filtering",
)
def get_audit_events(
    limit: int = Query(default=50, ge=1, le=500, description="Max events to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    decision: Optional[str] = Query(default=None, description="Filter by decision: ALLOW, REVIEW, BLOCK"),
    risk_level: Optional[str] = Query(default=None, description="Filter by risk level: LOW, MEDIUM, HIGH, CRITICAL"),
    anomaly_detected: Optional[bool] = Query(default=None, description="Filter by anomaly status"),
) -> List[AuditEventRecord]:
    """
    Query persistent audit events recorded by AgentGuard's interception layer.
    Supports filtering by decision, risk tier, and behavioral anomaly status.
    """
    service = get_audit_service()
    # Validate filter parameters if supplied
    if decision and decision.upper().strip() not in ("ALLOW", "REVIEW", "BLOCK"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision filter '{decision}'. Valid options: ALLOW, REVIEW, BLOCK.",
        )
    if risk_level and risk_level.upper().strip() not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid risk_level filter '{risk_level}'. Valid options: LOW, MEDIUM, HIGH, CRITICAL.",
        )

    return service.get_events(
        limit=limit,
        offset=offset,
        decision=decision,
        risk_level=risk_level,
        anomaly_detected=anomaly_detected,
    )


@router.get(
    "/events/{event_id}",
    response_model=AuditEventRecord,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a single audit event by database ID or interception ID",
)
def get_audit_event_detail(event_id: str) -> AuditEventRecord:
    """
    Retrieve full audit metadata for a specific event by its numeric database ID
    or string interception ID (e.g., AG-2026-4BB184C0).
    """
    service = get_audit_service()
    event = service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit event '{event_id}' not found.",
        )
    return event


@router.get(
    "/stats",
    response_model=AuditStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve summary metrics and distributions for the security dashboard",
)
def get_audit_statistics() -> AuditStatsResponse:
    """
    Computes real-time totals, averages, decision distributions, and risk breakdowns
    across all historical interception events.
    """
    service = get_audit_service()
    return service.get_stats()


@router.get(
    "/policies",
    response_model=Dict[str, int],
    status_code=status.HTTP_200_OK,
    summary="Retrieve frequency counts for triggered security policies",
)
def get_policy_statistics() -> Dict[str, int]:
    """
    Returns counts for all triggered security policies across all intercepted events,
    ordered by frequency descending.
    """
    service = get_audit_service()
    return service.get_policy_stats()
