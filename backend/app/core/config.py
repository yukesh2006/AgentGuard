"""
AgentGuard Core Configuration and Settings.
"""

import os
import json
import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Ensure project root is available in sys.path for ml module imports
APP_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _get_default_db_path() -> str:
    env_path = os.getenv("DATABASE_PATH") or os.getenv("DATABASE_URL")
    if env_path:
        if env_path.startswith("sqlite:///"):
            env_path = env_path[len("sqlite:///"):]
        return env_path
    return str(PROJECT_ROOT / "database" / "agentguard.db")


def _get_default_cors_origins() -> List[str]:
    base = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return base
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return list(dict.fromkeys(base + [str(x).strip() for x in parsed if str(x).strip()]))
    except Exception:
        pass
    items = [item.strip() for item in raw.split(",") if item.strip()]
    return list(dict.fromkeys(base + items))


class Settings(BaseModel):
    """Application configuration settings."""
    app_name: str = "AgentGuard"
    app_version: str = "0.3.0"
    description: str = "Context-Aware AI Intent Firewall"

    # Server Binding Settings
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # Database Settings
    database_path: str = Field(default_factory=_get_default_db_path)

    # CORS Settings for Frontend & Cloud Deployments
    cors_origins: List[str] = Field(default_factory=_get_default_cors_origins)

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


