"""
AgentGuard Safe Action Simulator.

Simulates agent action execution strictly within safe, in-memory sandboxed mock boundaries.
Under NO circumstances will this simulator execute real shell commands, delete local files,
read host credential files, or transmit outbound network requests.
"""

from typing import Dict, Any, Optional
from app.models.interception import SimulationStatusEnum


class SafeActionSimulator:
    """
    Simulates permitted actions with mock demonstration payloads and enforces
    strict guardrails preventing real-world execution.
    """

    @staticmethod
    def simulate(
        decision: str,
        action: str,
        target_resource: str,
        user_request: str = "",
    ) -> Dict[str, Any]:
        """
        Evaluate and return safe mock simulation state based on the security decision.
        """
        clean_decision = decision.upper().strip()

        # 1. Blocked Actions: Always halted without execution
        if clean_decision == "BLOCK":
            return {
                "simulation_status": SimulationStatusEnum.NOT_EXECUTED,
                "execution_permitted": False,
                "message": "Action blocked by AgentGuard before execution.",
                "simulation_output": None,
            }

        # 2. Actions Requiring Human Review: Paused pending approval
        if clean_decision == "REVIEW":
            return {
                "simulation_status": SimulationStatusEnum.WAITING_FOR_REVIEW,
                "execution_permitted": False,
                "message": "Human approval is required before the simulated action can proceed.",
                "simulation_output": None,
            }

        # 3. Allowed Actions: Safely mock operation without touching external/system resources
        if clean_decision == "ALLOW":
            # Safety Guardrail: Shell commands are never executed
            if action == "execute_command":
                return {
                    "simulation_status": SimulationStatusEnum.NOT_EXECUTED,
                    "execution_permitted": False,
                    "message": "System shell command execution is prohibited in this environment.",
                    "simulation_output": {"executed": False, "target": target_resource},
                }

            # Safety Guardrail: Destructive operations never modify filesystem
            if "delete" in action:
                return {
                    "simulation_status": SimulationStatusEnum.SIMULATION_ONLY,
                    "execution_permitted": True,
                    "message": "Destructive file deletion simulated in dry-run mode only; no file was modified or deleted.",
                    "simulation_output": {"dry_run": True, "target": target_resource, "deleted": False},
                }

            # Safety Guardrail: External network transfers never contact remote servers
            if "upload" in action or target_resource.startswith(("http://", "https://")):
                return {
                    "simulation_status": SimulationStatusEnum.NOT_EXECUTED,
                    "execution_permitted": False,
                    "message": "External network exfiltration is disabled.",
                    "simulation_output": {"transmitted": False, "target": target_resource},
                }

            # Safe Simulated File Read
            if action == "read_project_file":
                return {
                    "simulation_status": SimulationStatusEnum.SIMULATED_SUCCESS,
                    "execution_permitted": True,
                    "message": "Action allowed by AgentGuard and safely simulated.",
                    "simulation_output": {
                        "operation": "read_project_file",
                        "simulated_target": target_resource,
                        "simulated_records_found": 150,
                        "status": "simulated_read_ok",
                    },
                }

            # Safe Simulated Email Dispatch
            if action == "send_email":
                return {
                    "simulation_status": SimulationStatusEnum.SIMULATED_SUCCESS,
                    "execution_permitted": True,
                    "message": "Action allowed by AgentGuard and safely simulated.",
                    "simulation_output": {
                        "operation": "send_email",
                        "simulated_recipient": target_resource,
                        "dispatch_status": "simulated_sent_ok",
                    },
                }

            # Safe Simulated Report Generation
            if action == "generate_report":
                return {
                    "simulation_status": SimulationStatusEnum.SIMULATED_SUCCESS,
                    "execution_permitted": True,
                    "message": "Action allowed by AgentGuard and safely simulated.",
                    "simulation_output": {
                        "operation": "generate_report",
                        "simulated_report": f"Executive summary for: {user_request}",
                        "status": "simulated_report_ok",
                    },
                }

            # Safe Simulated Data Analysis
            if action == "analyze_data":
                return {
                    "simulation_status": SimulationStatusEnum.SIMULATED_SUCCESS,
                    "execution_permitted": True,
                    "message": "Action allowed by AgentGuard and safely simulated.",
                    "simulation_output": {
                        "operation": "analyze_data",
                        "simulated_metrics": {"row_count": 250, "summary": "normal"},
                        "status": "simulated_analysis_ok",
                    },
                }

            # Default safe mock response
            return {
                "simulation_status": SimulationStatusEnum.SIMULATED_SUCCESS,
                "execution_permitted": True,
                "message": f"Action allowed by AgentGuard and safely simulated.",
                "simulation_output": {
                    "operation": action,
                    "target": target_resource,
                    "status": "simulated_ok",
                },
            }

        # Fallback for unexpected states
        return {
            "simulation_status": SimulationStatusEnum.NOT_EXECUTED,
            "execution_permitted": False,
            "message": f"Unknown policy state '{decision}'; action halted.",
            "simulation_output": None,
        }
