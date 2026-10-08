"""
AgentGuard Behavioral Anomaly Detector.

Uses an IsolationForest model trained on a synthetic baseline of normal agent
execution trajectories to identify behavioral deviations, sudden tool escalations,
and abnormal sequences.

IMPORTANT METHODOLOGY NOTICE:
This anomaly detector uses a synthetic baseline representing typical routine agent
patterns (routine file reads, queries, data formatting, and benign repetition).
It is intended to demonstrate unsupervised anomaly detection methodology within
a security gateway prototype. A production deployment would require real-world
agent telemetry and empirical historical audit logs.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from ml.anomaly.features import BehavioralFeatureExtractor, FEATURE_NAMES


class BehavioralAnomalyDetector:
    """
    Lightweight behavioral anomaly detection service using IsolationForest.
    """

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self._model: Optional[IsolationForest] = None
        self._initialize_detector()

    def _generate_synthetic_baseline(self) -> np.ndarray:
        """
        Synthesize a baseline dataset reflecting normal routine agent behavior
        with realistic benign variance and rare baseline anomalies.
        """
        rng = np.random.RandomState(self.random_state)
        samples = []

        # 250 normal routine trajectories (reading files, analyses, queries, listings)
        for _ in range(250):
            history_len = rng.randint(0, 7)
            unique_count = max(1, int(history_len * rng.uniform(0.6, 1.0)))
            dest_h = rng.choice([0.0, 1.0], p=[0.97, 0.03])
            curr_dest = rng.choice([0.0, 1.0], p=[0.98, 0.02])
            ext_h = rng.choice([0.0, 1.0], p=[0.95, 0.05])
            curr_ext = rng.choice([0.0, 1.0], p=[0.96, 0.04])
            sys_h = rng.choice([0.0, 1.0], p=[0.98, 0.02])
            curr_sys = rng.choice([0.0, 1.0], p=[0.98, 0.02])
            repetition = rng.randint(0, 3)
            escalation = rng.choice([0.0, 1.0], p=[0.98, 0.02])

            samples.append([
                history_len,
                unique_count,
                dest_h,
                curr_dest,
                ext_h,
                curr_ext,
                sys_h,
                curr_sys,
                repetition,
                escalation,
            ])

        return np.array(samples, dtype=np.float32)

    def _initialize_detector(self) -> None:
        """
        Train the in-memory IsolationForest on the synthetic baseline.
        """
        X_train = self._generate_synthetic_baseline()
        self._model = IsolationForest(
            n_estimators=100,
            contamination=0.10,
            random_state=self.random_state,
        )
        self._model.fit(X_train)

    def detect_anomaly(
        self,
        previous_actions: List[str],
        current_action: str,
    ) -> Dict[str, Any]:
        """
        Extract behavioral features and compute the IsolationForest anomaly score.

        Returns:
            dict containing:
              - is_anomaly: bool
              - anomaly_score: float (positive = normal inlier, negative = anomalous outlier)
              - severity: "low", "medium", or "high"
        """
        if self._model is None:
            self._initialize_detector()

        feature_vector = BehavioralFeatureExtractor.extract_features(
            previous_actions=previous_actions,
            current_action=current_action,
        )

        # Reshape for scikit-learn (1, n_features)
        X = feature_vector.reshape(1, -1)

        decision_score = float(self._model.decision_function(X)[0])
        prediction = int(self._model.predict(X)[0])

        is_anomaly = bool(prediction == -1 or decision_score < 0.0)

        if not is_anomaly:
            severity = "low"
        elif decision_score < -0.08:
            severity = "high"
        else:
            severity = "medium"

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(decision_score, 4),
            "severity": severity,
        }


# Global singleton instance
_anomaly_detector = None


def get_anomaly_detector() -> BehavioralAnomalyDetector:
    """Singleton getter for BehavioralAnomalyDetector."""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = BehavioralAnomalyDetector()
    return _anomaly_detector
