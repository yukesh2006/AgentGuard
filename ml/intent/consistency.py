"""
AgentGuard Intent-Action Consistency Analyzer.

Evaluates semantic alignment between what the user requested and what action
an AI agent is attempting to execute, using sentence transformer embeddings.
"""

from typing import Dict, Any
from app.core.config import settings
from ml.intent.embeddings import get_embedding_service


class ConsistencyAnalyzer:
    """
    Compares user intent against proposed agent action using semantic similarity.
    """

    def __init__(self) -> None:
        self.embedding_service = get_embedding_service(
            model_name=settings.embedding_model_name
        )

    def evaluate_consistency(
        self,
        user_request: str,
        action_description: str,
        target_resource: str,
    ) -> Dict[str, Any]:
        """
        Compute semantic consistency between user request and the contextual action.

        Returns:
            dict containing:
              - similarity_score: float in [-1.0, 1.0] (rounded to 4 decimals)
              - compatibility: "high", "medium", or "low"
        """
        if not user_request or not user_request.strip():
            raise ValueError("User request cannot be empty.")
        if not action_description or not action_description.strip():
            raise ValueError("Action description cannot be empty.")

        # Construct contextualized action statement
        action_context = f"{action_description} on {target_resource}".strip()

        score = self.embedding_service.compute_similarity(
            user_request.strip(),
            action_context,
        )

        # Categorize according to configurable thresholds
        if score >= settings.high_similarity_threshold:
            compatibility = "high"
        elif score >= settings.low_similarity_threshold:
            compatibility = "medium"
        else:
            compatibility = "low"

        return {
            "similarity_score": score,
            "compatibility": compatibility,
        }


# Singleton instance
_consistency_analyzer = None


def get_consistency_analyzer() -> ConsistencyAnalyzer:
    """Singleton getter for the ConsistencyAnalyzer."""
    global _consistency_analyzer
    if _consistency_analyzer is None:
        _consistency_analyzer = ConsistencyAnalyzer()
    return _consistency_analyzer
