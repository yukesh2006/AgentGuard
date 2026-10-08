"""
AgentGuard Action Normalizer.

Maps agent tool actions into standardized, human-readable descriptions
and structural metadata for intent-action consistency analysis.
"""

from typing import Dict, NamedTuple, Optional


class ActionDefinition(NamedTuple):
    """Metadata describing a standardized agent action."""
    description: str
    category: str
    is_destructive: bool = False
    is_external: bool = False


# Catalog of 10 representative agent actions
ACTION_CATALOG: Dict[str, ActionDefinition] = {
    "read_project_file": ActionDefinition(
        description="Read a project data file",
        category="file_read",
        is_destructive=False,
        is_external=False,
    ),
    "delete_project_file": ActionDefinition(
        description="Delete a project data file",
        category="file_delete",
        is_destructive=True,
        is_external=False,
    ),
    "upload_external": ActionDefinition(
        description="Upload data to an external destination",
        category="network_upload",
        is_destructive=False,
        is_external=True,
    ),
    "send_email": ActionDefinition(
        description="Send an email",
        category="communication",
        is_destructive=False,
        is_external=True,
    ),
    "execute_command": ActionDefinition(
        description="Execute a system command",
        category="system_execution",
        is_destructive=False,
        is_external=False,
    ),
    "write_file": ActionDefinition(
        description="Write or modify a local file",
        category="file_write",
        is_destructive=False,
        is_external=False,
    ),
    "query_database": ActionDefinition(
        description="Query the internal database",
        category="database_query",
        is_destructive=False,
        is_external=False,
    ),
    "fetch_web_page": ActionDefinition(
        description="Fetch content from an external web page",
        category="network_fetch",
        is_destructive=False,
        is_external=True,
    ),
    "list_directory": ActionDefinition(
        description="List files in a directory",
        category="directory_inspect",
        is_destructive=False,
        is_external=False,
    ),
    "modify_permissions": ActionDefinition(
        description="Modify system or file permissions",
        category="security_config",
        is_destructive=False,
        is_external=False,
    ),
    "read_credentials_file": ActionDefinition(
        description="Read a credentials or authentication secrets file",
        category="credential_access",
        is_destructive=False,
        is_external=False,
    ),
}



def is_known_action(action_name: str) -> bool:
    """Check if the action exists in the normalized catalog."""
    return action_name in ACTION_CATALOG


def get_action_metadata(action_name: str) -> Optional[ActionDefinition]:
    """Retrieve detailed metadata for a given action."""
    return ACTION_CATALOG.get(action_name)


def normalize_action(action_name: str) -> Dict[str, str]:
    """
    Convert an agent action identifier into a normalized dictionary containing
    the standardized action name and its human-readable description.

    Raises:
        ValueError: If the action is not recognized in the catalog.
    """
    action_key = action_name.strip() if action_name else ""
    if not action_key:
        raise ValueError("Agent action identifier cannot be empty.")

    metadata = ACTION_CATALOG.get(action_key)
    if not metadata:
        supported = ", ".join(sorted(ACTION_CATALOG.keys()))
        raise ValueError(
            f"Unknown agent action '{action_key}'. Recognized actions are: {supported}"
        )

    return {
        "name": action_key,
        "description": metadata.description,
    }
