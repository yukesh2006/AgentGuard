"""
AgentGuard Behavioral Feature Extractor.

Extracts numerical behavioral representations from an agent's historical
action trajectory and current proposed action.
"""

from typing import List, Dict, Tuple
import numpy as np
from ml.intent.action_normalizer import get_action_metadata, is_known_action


FEATURE_NAMES = [
    "history_length",
    "unique_action_count",
    "destructive_history_count",
    "current_is_destructive",
    "external_history_count",
    "current_is_external",
    "system_command_history_count",
    "current_is_system_command",
    "action_repetition_count",
    "escalation_anomaly_flag",
]


class BehavioralFeatureExtractor:
    """
    Transforms action sequences and proposed actions into fixed-dimensional
    feature vectors for anomaly detection.
    """

    @staticmethod
    def extract_features(
        previous_actions: List[str],
        current_action: str,
    ) -> np.ndarray:
        """
        Extract a 10-dimensional feature vector.
        """
        feats_dict = BehavioralFeatureExtractor.extract_feature_dict(
            previous_actions=previous_actions,
            current_action=current_action,
        )
        return np.array([feats_dict[name] for name in FEATURE_NAMES], dtype=np.float32)

    @staticmethod
    def extract_feature_dict(
        previous_actions: List[str],
        current_action: str,
    ) -> Dict[str, float]:
        """
        Extract measurable behavioral signals into an explainable dictionary.
        """
        history = [a.strip() for a in previous_actions if a and a.strip()]
        current = current_action.strip() if current_action else ""

        current_meta = get_action_metadata(current)

        # 1. History volume
        history_len = float(len(history))

        # 2. Unique action variety
        unique_count = float(len(set(history)))

        # 3. Destructive history count
        destructive_history = 0.0
        for act in history:
            meta = get_action_metadata(act)
            if (meta and meta.is_destructive) or "delete" in act:
                destructive_history += 1.0

        # 4. Current action destructive flag
        current_is_destructive = 1.0 if (
            (current_meta and current_meta.is_destructive) or "delete" in current
        ) else 0.0

        # 5. External transfer history count
        external_history = 0.0
        for act in history:
            meta = get_action_metadata(act)
            if (meta and meta.is_external) or "upload" in act:
                external_history += 1.0

        # 6. Current action external flag
        current_is_external = 1.0 if (
            (current_meta and current_meta.is_external) or "upload" in current
        ) else 0.0

        # 7. System command history count
        sys_cmd_history = float(sum(1 for act in history if act == "execute_command"))

        # 8. Current action system command flag
        current_is_sys_cmd = 1.0 if current == "execute_command" else 0.0

        # 9. Action repetition count in history
        repetition_count = float(sum(1 for act in history if act == current))

        # 10. Escalation flag: benign history followed by sudden dangerous/system command
        escalation = 0.0
        if history_len > 0 and destructive_history == 0.0 and sys_cmd_history == 0.0:
            if current_is_destructive == 1.0 or current_is_sys_cmd == 1.0:
                escalation = 1.0

        return {
            "history_length": history_len,
            "unique_action_count": unique_count,
            "destructive_history_count": destructive_history,
            "current_is_destructive": current_is_destructive,
            "external_history_count": external_history,
            "current_is_external": current_is_external,
            "system_command_history_count": sys_cmd_history,
            "current_is_system_command": current_is_sys_cmd,
            "action_repetition_count": repetition_count,
            "escalation_anomaly_flag": escalation,
        }
