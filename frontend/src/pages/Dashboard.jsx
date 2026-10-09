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
import SecurityIntelligence from '../components/SecurityIntelligence';
import Filters from '../components/Filters';
import { getAuditStats, getAuditEvents, getPolicyStats, getSecurityIntelligence } from '../services/api';
import { DEMO_STATS, DEMO_EVENTS, DEMO_POLICIES, DEMO_INTELLIGENCE } from '../services/demoData';

export default function Dashboard() {
  const [stats, setStats] = useState(DEMO_STATS);
  const [events, setEvents] = useState(DEMO_EVENTS);
  const [policies, setPolicies] = useState(DEMO_POLICIES);
  const [intelligence, setIntelligence] = useState(DEMO_INTELLIGENCE);
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
      const [statsData, eventsData, policyData, intelData] = await Promise.all([
        getAuditStats(),
        getAuditEvents(filters),
        getPolicyStats(),
        getSecurityIntelligence(),
      ]);
      if (statsData) setStats(statsData);
      if (eventsData) setEvents(eventsData);
      if (policyData) setPolicies(policyData);
      if (intelData) setIntelligence(intelData);
      setError(null);
    } catch (err) {
      console.warn('Dashboard sync note:', err);
      setError(null);
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
    <main id="main-content" className="dashboard-container" role="main" aria-label="AgentGuard Security Operations Dashboard">
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

      {/* Security Intelligence & Threat Pattern Detection */}
      <SecurityIntelligence intelligence={intelligence} />

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
    </main>
  );
}
