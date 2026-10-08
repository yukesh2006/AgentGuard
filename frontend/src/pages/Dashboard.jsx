import React, { useState, useEffect, useCallback } from 'react';
import Header from '../components/Header';
import StatCard from '../components/StatCard';
import RiskChart from '../components/RiskChart';
import DecisionChart from '../components/DecisionChart';
import EventTable from '../components/EventTable';
import EventDetails from '../components/EventDetails';
import SecurityTimeline from '../components/SecurityTimeline';
import PolicySummary from '../components/PolicySummary';
import ActionSimulator from '../components/ActionSimulator';
import Filters from '../components/Filters';
import { getAuditStats, getAuditEvents, getPolicyStats } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_events: 0,
    allowed: 0,
    review: 0,
    blocked: 0,
    average_risk_score: 0.0,
    high_risk_events: 0,
    critical_events: 0,
    anomalous_events: 0,
    risk_distribution: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
    decision_distribution: { ALLOW: 0, REVIEW: 0, BLOCK: 0 },
  });

  const [events, setEvents] = useState([]);
  const [policies, setPolicies] = useState({});
  const [filters, setFilters] = useState({
    decision: 'ALL',
    risk_level: 'ALL',
    anomaly_detected: 'ALL',
    limit: 50,
  });

  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load all dashboard metrics
  const loadDashboardData = useCallback(async (isSilent = false) => {
    if (!isSilent) setLoading(true);
    try {
      const [statsData, eventsData, policyData] = await Promise.all([
        getAuditStats(),
        getAuditEvents(filters),
        getPolicyStats(),
      ]);
      setStats(statsData);
      setEvents(eventsData);
      setPolicies(policyData);
      setError(null);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Unable to connect to AgentGuard backend. Verify FastAPI is running at http://127.0.0.1:8000.');
    } finally {
      if (!isSilent) setLoading(false);
    }
  }, [filters]);

  // Initial load and filter change
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Automatic periodic polling every 15s
  useEffect(() => {
    const timer = setInterval(() => {
      loadDashboardData(true);
    }, 15000);
    return () => clearInterval(timer);
  }, [loadDashboardData]);

  return (
    <div className="dashboard-container">
      <Header onRefresh={() => loadDashboardData(false)} loading={loading} />

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button
            onClick={() => loadDashboardData(false)}
            style={{ background: 'transparent', border: '1px solid #fca5a5', color: '#fca5a5', padding: '0.2rem 0.6rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.75rem' }}
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Top Security Overview Stats */}
      <div className="stats-grid">
        <StatCard
          title="Total Interceptions"
          value={stats.total_events}
          subtext={`Avg Risk: ${stats.average_risk_score.toFixed(1)}/100`}
          type="total"
        />
        <StatCard
          title="Allowed Actions"
          value={stats.allowed}
          subtext={`${stats.total_events ? Math.round((stats.allowed / stats.total_events) * 100) : 0}% of traffic`}
          type="allow"
        />
        <StatCard
          title="Under Review"
          value={stats.review}
          subtext="HITL confirmation queue"
          type="review"
        />
        <StatCard
          title="Blocked Threats"
          value={stats.blocked}
          subtext="Immediate policy termination"
          type="block"
        />
        <StatCard
          title="High / Critical Threats"
          value={stats.high_risk_events + stats.critical_events}
          subtext={`${stats.anomalous_events} behavioral anomalies`}
          type="highrisk"
        />
      </div>

      {/* Live Agent Action Simulator (Hackathon Judge Testing Sandbox) */}
      <ActionSimulator onInterceptionComplete={() => loadDashboardData(true)} />

      {/* Security Analytics Visual Charts */}
      <div className="charts-grid">
        <RiskChart
          distribution={stats.risk_distribution}
          total={stats.total_events}
        />
        <DecisionChart
          distribution={stats.decision_distribution}
          total={stats.total_events}
        />
      </div>

      {/* Timeline & Policy Analytics Grid */}
      <div className="charts-grid">
        <SecurityTimeline
          events={events}
          onSelectEvent={(evt) => setSelectedEvent(evt)}
        />
        <PolicySummary policies={policies} />
      </div>

      {/* Audit Events Log Table Section */}
      <div className="dashboard-card">
        <div className="card-title">
          <span>Recent Interception Events</span>
          <span className="card-subtitle">Showing {events.length} persistent audit records</span>
        </div>

        <Filters filters={filters} onChange={setFilters} />

        <EventTable
          events={events}
          onSelectEvent={(evt) => setSelectedEvent(evt)}
        />
      </div>

      {/* Audit Detail Modal */}
      {selectedEvent && (
        <EventDetails
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </div>
  );
}
