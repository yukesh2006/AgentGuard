"""
AgentGuard Core Configuration and Settings.
"""

import sys
from pathlib import Path
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
    app_version: str = "0.2.0"
    description: str = "Context-Aware AI Intent Firewall"

    # ML / Embedding Settings
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # Intent-Action Consistency Thresholds
    # Scores >= high_threshold: "high"
    # Scores between low_threshold and high_threshold: "medium"
    # Scores < low_threshold: "low"
    high_similarity_threshold: float = 0.33
    low_similarity_threshold: float = 0.15



settings = Settings()
