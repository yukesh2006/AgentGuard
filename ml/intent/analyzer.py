"""
AgentGuard Intent Analyzer.

Analyzes natural-language user instructions to determine user goal,
classify intent category, and calculate confidence using sentence embeddings.
"""

from typing import Dict, Any, List
import re
from ml.intent.embeddings import get_embedding_service


# Canonical intent categories with representative semantic anchors
INTENT_PROTOTYPES: Dict[str, List[str]] = {
    "report_generation": [
        "prepare my monthly project report",
        "generate quarterly project status report",
        "compile analytics summary and document results",
        "draft monthly performance review report",
    ],
    "data_analysis": [
        "analyze project dataset and compute metrics",
        "evaluate statistical data and charts",
        "inspect numbers and calculate summaries",
    ],
    "file_management": [
        "organize directory files and archive records",
        "clean workspace files and manage folder structure",
        "backup project files to storage",
    ],
    "communication_dispatch": [
        "send email to recipient or professor",
        "notify team members via email dispatch",
        "forward completed report to advisor",
        "send an email message with attachment",
    ],
    "system_administration": [
        "execute system command in terminal",
        "run shell utility and manage server processes",
        "inspect operating system status",
    ],
    "information_retrieval": [
        "search project documentation and read guidelines",
        "query knowledge base and lookup reference notes",
    ],
}


class IntentAnalyzer:
    """
    Transforms natural-language user requests into structured intent objects
    using semantic embedding comparisons.
    """

    def __init__(self) -> None:
        self.embedding_service = get_embedding_service()
        # Pre-compute prototype anchor strings for each intent category
        self._prototype_texts = {
            category: " ".join(phrases)
            for category, phrases in INTENT_PROTOTYPES.items()
        }

    def _extract_goal(self, user_request: str) -> str:
        """
        Normalize and extract the primary goal description from the request.
        """
        cleaned = user_request.strip()
        # Remove common introductory conversational prefixes
        pattern = r"^(please|could you|can you|kindly|i want to|help me)\s+"
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
        return cleaned if cleaned else user_request.strip()

    def analyze(self, user_request: str) -> Dict[str, Any]:
        """
        Analyze a user request and return:
          - intent: classified category
          - goal: extracted goal string
          - confidence: real calculated cosine similarity score
        """
        if not user_request or not user_request.strip():
            raise ValueError("User request cannot be empty.")

        goal = self._extract_goal(user_request)

        # Compute similarity between user request and each intent category
        best_intent = "general_task"
        highest_score = -1.0

        for category, prototype_text in self._prototype_texts.items():
            sim = self.embedding_service.compute_similarity(user_request, prototype_text)
            if sim > highest_score:
                highest_score = sim
                best_intent = category

        # Bound confidence to [0.0, 1.0]
        confidence = max(0.0, min(1.0, highest_score))

        return {
            "intent": best_intent,
            "goal": goal,
            "confidence": round(confidence, 4),
        }


# Global helper instance
_intent_analyzer = None


def get_intent_analyzer() -> IntentAnalyzer:
    """Singleton getter for the IntentAnalyzer."""
    global _intent_analyzer
    if _intent_analyzer is None:
        _intent_analyzer = IntentAnalyzer()
    return _intent_analyzer
