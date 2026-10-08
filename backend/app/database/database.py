"""
AgentGuard Database Connection & Initialization Manager.
Phase 6: SQLite Audit Database.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from app.core.config import settings

# Embedded DDL for zero-dependency initialization
INIT_SQL = """
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interception_id TEXT UNIQUE NOT NULL,
    timestamp TEXT NOT NULL,
    user_goal TEXT NOT NULL,
    action TEXT NOT NULL,
    target_resource TEXT NOT NULL,
    destination TEXT,
    decision TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    explanation TEXT NOT NULL,
    triggered_policies TEXT NOT NULL,
    simulation_status TEXT NOT NULL,
    execution_permitted INTEGER NOT NULL,
    review_status TEXT NOT NULL,
    anomaly_detected INTEGER NOT NULL DEFAULT 0,
    intent_similarity REAL DEFAULT NULL,
    simulation_output TEXT DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_decision ON audit_events(decision);
CREATE INDEX IF NOT EXISTS idx_audit_risk_level ON audit_events(risk_level);
CREATE INDEX IF NOT EXISTS idx_audit_anomaly ON audit_events(anomaly_detected);
CREATE INDEX IF NOT EXISTS idx_audit_interception_id ON audit_events(interception_id);
"""


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Return configured or custom SQLite database file path."""
    if custom_path:
        return custom_path
    return settings.database_path


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Produce a SQLite connection configured with Row factory
    and automatic directory creation.
    """
    path_str = get_db_path(db_path)
    if path_str != ":memory:":
        db_file = Path(path_str)
        db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path_str, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize SQLite database schema and indexes.
    Idempotent: safe to run multiple times.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.executescript(INIT_SQL)
    finally:
        conn.close()
