"""
AgentGuard Core Configuration and Settings.
"""

import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel

# Ensure project root is available in sys.path for ml module imports
APP_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class Settings(BaseModel):
    """Application configuration settings."""
    app_name: str = "AgentGuard"
    app_version: str = "0.3.0"
    description: str = "Context-Aware AI Intent Firewall"

    # Database Settings
    database_path: str = str(PROJECT_ROOT / "database" / "agentguard.db")

    # CORS Settings for Frontend
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ML / Embedding Settings
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Intent-Action Consistency Thresholds
    # Scores >= high_threshold: "high"
    # Scores between low_threshold and high_threshold: "medium"
    # Scores < low_threshold: "low"
    high_similarity_threshold: float = 0.33
    low_similarity_threshold: float = 0.15

    # Risk Level Categorization Thresholds (0 - 100)
    risk_level_low_threshold: float = 25.0       # < 25: LOW
    risk_level_medium_threshold: float = 50.0    # 25 to < 50: MEDIUM
    risk_level_high_threshold: float = 75.0      # 50 to < 75: HIGH
    # >= 75: CRITICAL

    # Prototype Risk Factor Weights (Centralized)
    weight_intent_inconsistency: float = 25.0
    weight_behavioral_anomaly: float = 20.0
    weight_destructive_action: float = 25.0
    weight_external_transfer: float = 25.0
    weight_system_execution: float = 25.0
    weight_resource_sensitivity: float = 25.0
    weight_permission_mismatch: float = 15.0


settings = Settings()

