"""
AgentGuard Resource Sensitivity Classifier.

Provides transparent heuristics to classify target resources into sensitivity
tiers (sensitive credentials, normal project files, external URLs, etc.).
"""

from typing import Dict, Any
import re


SENSITIVE_KEYWORD_PATTERNS = (
    "credential", "password", "secret", "private_key", "id_rsa",
    "api_key", "auth_token", "jwt", ".env", "shadow", "passwd",
)

SYSTEM_RESOURCE_PATTERNS = (
    "bash", "sh", "cmd", "powershell", "/bin/", "/usr/bin/",
    "/dev/", "terminal", "system32", "kernel",
)


def classify_resource(resource: str) -> Dict[str, Any]:
    """
    Classify a target resource string into a sensitivity tier.

    Returns:
        dict containing:
          - category: str
          - is_sensitive: bool
          - description: str
    """
    res = resource.strip().lower()

    # 1. Check for sensitive credentials and keys
    if any(pat in res for pat in SENSITIVE_KEYWORD_PATTERNS):
        return {
            "category": "sensitive_credentials",
            "is_sensitive": True,
            "description": "High-sensitivity asset containing secrets, passwords, or authentication keys.",
        }

    # 2. Check for system shell and process targets
    if any(pat in res for pat in SYSTEM_RESOURCE_PATTERNS):
        return {
            "category": "system_resource",
            "is_sensitive": True,
            "description": "Operating system process or administrative command interface.",
        }

    # 3. Check for external network destinations
    if res.startswith(("http://", "https://", "ftp://", "wss://")):
        return {
            "category": "external_destination",
            "is_sensitive": False,
            "description": "External network URL or remote service endpoint.",
        }

    # 4. Check for email addresses
    if re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", res):
        return {
            "category": "email_destination",
            "is_sensitive": False,
            "description": "External email communication recipient.",
        }

    # 5. Check for database resources
    if res.endswith((".db", ".sqlite", ".sqlite3")) or "database" in res:
        return {
            "category": "database_resource",
            "is_sensitive": False,
            "description": "Local or internal database store.",
        }

    # 6. Check for standard documents
    if res.endswith((".pdf", ".docx", ".pptx", ".md", ".html")):
        return {
            "category": "normal_document",
            "is_sensitive": False,
            "description": "Standard document or presentation file.",
        }

    # 7. Check for typical project data files
    if res.endswith((".csv", ".tsv", ".json", ".txt", ".parquet", ".xlsx")):
        return {
            "category": "normal_project_file",
            "is_sensitive": False,
            "description": "Standard internal project data or tabular file.",
        }

    # Default fallback
    return {
        "category": "general_resource",
        "is_sensitive": False,
        "description": "General or unclassified resource target.",
    }
