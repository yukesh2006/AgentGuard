"""
AgentGuard Context Engine.

Extracts, structures, and enriches operational context from incoming requests,
including resource classification, user permissions, and session history.
"""

from typing import Dict, Any, Optional, List
import re


FILE_EXTENSIONS = (
    ".csv", ".tsv", ".json", ".txt", ".pdf", ".md", ".py", ".yaml",
    ".yml", ".xml", ".docx", ".xlsx", ".log", ".sql", ".html"
)


class ContextEngine:
    """
    Structured context extraction engine for AgentGuard requests.
    """

    @staticmethod
    def infer_resource_type(resource: str, explicit_type: Optional[str] = None) -> str:
        """
        Deduce the resource category (file, network_endpoint, email, database, etc.)
        from the resource target string unless an explicit type is supplied.
        """
        if explicit_type and explicit_type.strip():
            return explicit_type.strip().lower()

        res = resource.strip().lower()

        # Check for URLs / network destinations
        if res.startswith(("http://", "https://", "ftp://", "wss://", "ws://")):
            return "network_endpoint"

        # Check for email addresses
        if re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", res):
            return "email_recipient"

        # Check for database files or identifiers
        if res.endswith((".db", ".sqlite", ".sqlite3")) or "database" in res:
            return "database"

        # Check for local file extensions
        if any(res.endswith(ext) for ext in FILE_EXTENSIONS) or "/" in res or "\\" in res:
            return "file"

        # Default fallback
        return "general_resource"

    def process_context(
        self,
        goal: str,
        target_resource: str,
        agent_action: str,
        explicit_resource_type: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        previous_actions: Optional[List[str]] = None,
        user_permissions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Construct a structured operational context payload.
        """
        res_type = self.infer_resource_type(
            resource=target_resource,
            explicit_type=explicit_resource_type,
        )

        permissions = user_permissions if user_permissions else ["standard_user"]
        history = previous_actions if previous_actions else []

        return {
            "goal": goal,
            "resource": target_resource,
            "action": agent_action,
            "resource_type": res_type,
            "session_id": session_id,
            "user_id": user_id,
            "previous_actions": history,
            "user_permissions": permissions,
        }


# Singleton instance
_context_engine = None


def get_context_engine() -> ContextEngine:
    """Singleton getter for the ContextEngine."""
    global _context_engine
    if _context_engine is None:
        _context_engine = ContextEngine()
    return _context_engine
