-- ==============================================================================
-- AgentGuard - SQLite Audit Database Schema (Phase 6)
-- Persistent storage for security interception events and policy decisions
-- ==============================================================================

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
    triggered_policies TEXT NOT NULL, -- JSON serialized list of strings
    simulation_status TEXT NOT NULL,
    execution_permitted INTEGER NOT NULL, -- 0 or 1
    review_status TEXT NOT NULL,
    anomaly_detected INTEGER NOT NULL DEFAULT 0, -- 0 or 1
    intent_similarity REAL DEFAULT NULL,
    simulation_output TEXT DEFAULT NULL -- JSON serialized dictionary or null
);

-- Indexes for high-performance dashboard querying and analytics
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_decision ON audit_events(decision);
CREATE INDEX IF NOT EXISTS idx_audit_risk_level ON audit_events(risk_level);
CREATE INDEX IF NOT EXISTS idx_audit_anomaly ON audit_events(anomaly_detected);
CREATE INDEX IF NOT EXISTS idx_audit_interception_id ON audit_events(interception_id);
