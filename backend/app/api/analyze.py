"""
AgentGuard API Router: /analyze Endpoint.

Processes incoming agent action proposals against user intent and contextual
metadata to evaluate semantic consistency and security signals.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    IntentResult,
    ContextResult,
    ActionInfo,
    ConsistencyResult,
    SecuritySignal,
)
from ml.intent.action_normalizer import normalize_action
from ml.intent.analyzer import get_intent_analyzer
from ml.intent.consistency import get_consistency_analyzer
from ml.context.engine import get_context_engine
from app.services.signals import evaluate_security_signals

router = APIRouter(tags=["Analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze agent action proposal against user intent",
)
def analyze_action(payload: AnalyzeRequest) -> AnalyzeResponse:
    """
    Evaluates whether an AI agent's proposed action is semantically consistent
    with the original user intent, extracting operational context and
    generating contextual security signals.
    """
    # 1. Action Normalization & Validation
    try:
        action_dict = normalize_action(payload.agent_action)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # 2. Intent Analysis
    try:
        intent_analyzer = get_intent_analyzer()
        intent_dict = intent_analyzer.analyze(payload.user_request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent analysis service error: {exc}",
        ) from exc

    # 3. Context Processing
    try:
        context_engine = get_context_engine()
        context_dict = context_engine.process_context(
            goal=intent_dict["goal"],
            target_resource=payload.target_resource,
            agent_action=action_dict["name"],
            explicit_resource_type=payload.resource_type,
            session_id=payload.session_id,
            user_id=payload.user_id,
            previous_actions=payload.previous_actions,
            user_permissions=payload.user_permissions,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context engine error: {exc}",
        ) from exc

    # 4. Intent-Action Consistency Analysis
    try:
        consistency_analyzer = get_consistency_analyzer()
        consistency_dict = consistency_analyzer.evaluate_consistency(
            user_request=payload.user_request,
            action_description=action_dict["description"],
            target_resource=payload.target_resource,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Consistency evaluation error: {exc}",
        ) from exc

    # 5. Security Signals Generation
    signal_dicts = evaluate_security_signals(
        user_request=payload.user_request,
        intent_info=intent_dict,
        context_info=context_dict,
        action_info=action_dict,
        consistency_info=consistency_dict,
    )

    # 6. Structured Response Construction
    return AnalyzeResponse(
        intent=IntentResult(**intent_dict),
        context=ContextResult(**context_dict),
        action=ActionInfo(**action_dict),
        consistency=ConsistencyResult(**consistency_dict),
        signals=[SecuritySignal(**s) for s in signal_dicts],
    )
