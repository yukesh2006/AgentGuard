"""
AgentGuard Contextual Security Signals Service.

Generates rule-based contextual security signals based on intent, context,
action metadata, and semantic compatibility.

Note: These signals inform the analysis; they do NOT make final
ALLOW/REVIEW/BLOCK policy decisions.
"""

from typing import List, Dict, Any
from ml.intent.action_normalizer import get_action_metadata


def evaluate_security_signals(
    user_request: str,
    intent_info: Dict[str, Any],
    context_info: Dict[str, Any],
    action_info: Dict[str, Any],
    consistency_info: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Produce a list of structured security signals evaluating contextual risk factors.
    """
    signals: List[Dict[str, str]] = []
    action_name = action_info.get("name", "")
    metadata = get_action_metadata(action_name)
    request_lower = user_request.lower()
    compatibility = consistency_info.get("compatibility", "low")
    intent_category = intent_info.get("intent", "")

    # 1. Intent-Action Semantic Consistency Signal
    if compatibility == "high":
        signals.append({
            "type": "intent_action_consistency",
            "severity": "low",
            "description": "The requested action is consistent with the user's goal.",
        })
    elif compatibility == "medium":
        signals.append({
            "type": "intent_action_consistency",
            "severity": "medium",
            "description": "Moderate semantic compatibility: the action is somewhat related to the goal but requires attention.",
        })
    else:
        signals.append({
            "type": "intent_action_consistency",
            "severity": "high",
            "description": "Low semantic compatibility: the agent action diverges significantly from the stated user intent.",
        })

    # 2. Destructive Action Signal
    is_destructive = metadata.is_destructive if metadata else ("delete" in action_name)
    deletion_keywords = ("delete", "remove", "clean", "purge", "erase", "destroy")
    request_asks_deletion = any(kw in request_lower for kw in deletion_keywords)

    if is_destructive:
        if not request_asks_deletion:
            signals.append({
                "type": "destructive_action_anomaly",
                "severity": "high",
                "description": (
                    f"Action '{action_name}' is destructive, but user goal does not request file or resource deletion."
                ),
            })
        else:
            signals.append({
                "type": "destructive_action_requested",
                "severity": "medium",
                "description": "Destructive operation requested in direct alignment with user instructions.",
            })

    # 3. External Data Transfer / Exfiltration Signal
    is_external_upload = action_name == "upload_external" or (
        metadata and metadata.is_external and "upload" in action_name
    )
    external_transfer_keywords = ("upload", "publish", "transfer to external", "send to external server")
    request_asks_upload = any(kw in request_lower for kw in external_transfer_keywords)

    if is_external_upload:
        if not request_asks_upload:
            signals.append({
                "type": "external_data_transfer",
                "severity": "high",
                "description": (
                    "Attempting to upload data to an external destination without explicit authorization in user intent."
                ),
            })
        else:
            signals.append({
                "type": "external_data_transfer_authorized",
                "severity": "low",
                "description": "External data transfer initiated as requested by the user.",
            })

    # 4. System Command Execution Signal
    if action_name == "execute_command":
        sys_admin_keywords = ("run command", "terminal", "bash", "execute script", "cli", "system")
        if intent_category != "system_administration" and not any(kw in request_lower for kw in sys_admin_keywords):
            signals.append({
                "type": "unrelated_system_execution",
                "severity": "high",
                "description": (
                    "Execution of arbitrary system shell command does not align with non-administrative user request."
                ),
            })

    # 5. Safe Resource Access Signal
    if action_name in ("read_project_file", "list_directory") and compatibility in ("high", "medium"):
        signals.append({
            "type": "authorized_resource_access",
            "severity": "low",
            "description": "Safe, non-destructive access to internal workspace resource.",
        })

    # 6. Communication Dispatch Signal
    if action_name == "send_email":
        comm_keywords = ("send", "email", "mail", "notify", "professor", "forward", "share")
        if any(kw in request_lower for kw in comm_keywords):
            signals.append({
                "type": "communication_dispatch_aligned",
                "severity": "low",
                "description": "Communication dispatch aligns directly with user instructions.",
            })
        else:
            signals.append({
                "type": "unexpected_communication_dispatch",
                "severity": "medium",
                "description": "Attempting external communication without explicit communication request in user intent.",
            })

    return signals
