"""
AgentGuard Audit Repository.
Phase 6: Data access operations for persistent SQLite audit logs.
"""

import json
from typing import List, Optional, Dict, Any
from app.database.database import get_db_connection, init_db
from app.database.models import AuditEventRecord, AuditEventCreate, AuditStatsResponse


class AuditRepository:
    """
    Data Access Object (DAO) executing parameterized queries on SQLite.
    Separates database storage from application business logic.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path
        # Auto-initialize database tables if not existing
        init_db(self.db_path)

    def _row_to_record(self, row) -> AuditEventRecord:
        """Convert a sqlite3.Row into a typed AuditEventRecord."""
        triggered = []
        if row["triggered_policies"]:
            try:
                triggered = json.loads(row["triggered_policies"])
            except Exception:
                triggered = [row["triggered_policies"]]

        sim_output = None
        if row["simulation_output"]:
            try:
                sim_output = json.loads(row["simulation_output"])
            except Exception:
                sim_output = None

        return AuditEventRecord(
            id=row["id"],
            interception_id=row["interception_id"],
            timestamp=row["timestamp"],
            user_goal=row["user_goal"],
            action=row["action"],
            target_resource=row["target_resource"],
            destination=row["destination"],
            decision=row["decision"],
            risk_score=float(row["risk_score"]),
            risk_level=row["risk_level"],
            explanation=row["explanation"],
            triggered_policies=triggered,
            simulation_status=row["simulation_status"],
            execution_permitted=bool(row["execution_permitted"]),
            review_status=row["review_status"],
            anomaly_detected=bool(row["anomaly_detected"]),
            intent_similarity=float(row["intent_similarity"]) if row["intent_similarity"] is not None else None,
            simulation_output=sim_output,
        )

    def create_event(self, event: AuditEventCreate) -> AuditEventRecord:
        """Insert a new audit event into the SQLite database."""
        conn = get_db_connection(self.db_path)
        query = """
        INSERT INTO audit_events (
            interception_id, timestamp, user_goal, action, target_resource,
            destination, decision, risk_score, risk_level, explanation,
            triggered_policies, simulation_status, execution_permitted,
            review_status, anomaly_detected, intent_similarity, simulation_output
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            event.interception_id,
            event.timestamp,
            event.user_goal,
            event.action,
            event.target_resource,
            event.destination,
            event.decision.upper(),
            event.risk_score,
            event.risk_level.upper(),
            event.explanation,
            json.dumps(event.triggered_policies),
            event.simulation_status,
            1 if event.execution_permitted else 0,
            event.review_status,
            1 if event.anomaly_detected else 0,
            event.intent_similarity,
            json.dumps(event.simulation_output) if event.simulation_output else None,
        )

        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                new_id = cursor.lastrowid
            return self.get_event_by_id(new_id)  # type: ignore
        finally:
            conn.close()

    def get_event_by_id(self, event_id: int) -> Optional[AuditEventRecord]:
        """Fetch single event by auto-increment ID."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
            return None
        finally:
            conn.close()

    def get_event_by_interception_id(self, interception_id: str) -> Optional[AuditEventRecord]:
        """Fetch single event by its unique interception identifier (e.g. AG-2026-XXXX)."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM audit_events WHERE interception_id = ?", (interception_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
            return None
        finally:
            conn.close()

    def get_events(
        self,
        limit: int = 50,
        offset: int = 0,
        decision: Optional[str] = None,
        risk_level: Optional[str] = None,
        anomaly_detected: Optional[bool] = None,
    ) -> List[AuditEventRecord]:
        """Query audit events with optional filtering, sorted newest first."""
        conn = get_db_connection(self.db_path)
        conditions = []
        params: List[Any] = []

        if decision:
            conditions.append("decision = ?")
            params.append(decision.upper().strip())

        if risk_level:
            conditions.append("risk_level = ?")
            params.append(risk_level.upper().strip())

        if anomaly_detected is not None:
            conditions.append("anomaly_detected = ?")
            params.append(1 if anomaly_detected else 0)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        sql = f"""
        SELECT * FROM audit_events
        {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """
        params.extend([max(1, limit), max(0, offset)])

        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [self._row_to_record(r) for r in rows]
        finally:
            conn.close()

    def get_stats(self) -> AuditStatsResponse:
        """Compute aggregated security metrics across all audit events."""
        conn = get_db_connection(self.db_path)
        try:
            cursor = conn.cursor()

            # Total and averages
            cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COALESCE(AVG(risk_score), 0.0) as avg_risk,
                SUM(CASE WHEN anomaly_detected = 1 THEN 1 ELSE 0 END) as anomalies
            FROM audit_events
            """)
            summary_row = cursor.fetchone()
            total = summary_row["total"] or 0
            avg_risk = round(summary_row["avg_risk"] or 0.0, 1)
            anomalies = summary_row["anomalies"] or 0

            # Decisions
            cursor.execute("SELECT decision, COUNT(*) as count FROM audit_events GROUP BY decision")
            dec_counts = {r["decision"]: r["count"] for r in cursor.fetchall()}

            # Risk levels
            cursor.execute("SELECT risk_level, COUNT(*) as count FROM audit_events GROUP BY risk_level")
            risk_counts = {r["risk_level"]: r["count"] for r in cursor.fetchall()}

            allowed = dec_counts.get("ALLOW", 0)
            review = dec_counts.get("REVIEW", 0)
            blocked = dec_counts.get("BLOCK", 0)

            low = risk_counts.get("LOW", 0)
            med = risk_counts.get("MEDIUM", 0)
            high = risk_counts.get("HIGH", 0)
            crit = risk_counts.get("CRITICAL", 0)

            return AuditStatsResponse(
                total_events=total,
                allowed=allowed,
                review=review,
                blocked=blocked,
                average_risk_score=avg_risk,
                high_risk_events=high,
                critical_events=crit,
                anomalous_events=anomalies,
                risk_distribution={"LOW": low, "MEDIUM": med, "HIGH": high, "CRITICAL": crit},
                decision_distribution={"ALLOW": allowed, "REVIEW": review, "BLOCK": blocked},
            )
        finally:
            conn.close()

    def get_policy_stats(self) -> Dict[str, int]:
        """Aggregate frequencies of triggered policies across all audit records."""
        conn = get_db_connection(self.db_path)
        counts: Dict[str, int] = {}
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT triggered_policies FROM audit_events")
            for row in cursor.fetchall():
                raw = row["triggered_policies"]
                if not raw:
                    continue
                try:
                    policies = json.loads(raw)
                    if isinstance(policies, list):
                        for p in policies:
                            counts[p] = counts.get(p, 0) + 1
                except Exception:
                    continue

            # Return sorted by highest count first
            return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
        finally:
            conn.close()


# Singleton repository instance
_audit_repo: Optional[AuditRepository] = None


def get_audit_repository(db_path: Optional[str] = None) -> AuditRepository:
    """Singleton getter for AuditRepository."""
    global _audit_repo
    if _audit_repo is None or (db_path and _audit_repo.db_path != db_path):
        _audit_repo = AuditRepository(db_path=db_path)
    return _audit_repo
