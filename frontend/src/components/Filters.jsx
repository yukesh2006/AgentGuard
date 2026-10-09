import React from 'react';

export default function Filters({ filters, onChange }) {
  const handleDecision = (e) => onChange({ ...filters, decision: e.target.value });
  const handleRisk = (e) => onChange({ ...filters, risk_level: e.target.value });
  const handleAnomaly = (e) => onChange({ ...filters, anomaly_detected: e.target.value });

  const resetFilters = () => onChange({ decision: 'ALL', risk_level: 'ALL', anomaly_detected: 'ALL' });

  const hasActiveFilters = filters.decision !== 'ALL' || filters.risk_level !== 'ALL' || filters.anomaly_detected !== 'ALL';

  return (
    <div className="filter-bar" role="search" aria-label="Audit Events Filter Toolbar">
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', alignItems: 'center' }}>
        <div className="filter-group">
          <label htmlFor="filter-decision">Decision:</label>
          <select
            id="filter-decision"
            className="filter-select"
            value={filters.decision}
            onChange={handleDecision}
            aria-label="Filter events by decision verdict"
          >
            <option value="ALL">All Decisions</option>
            <option value="ALLOW">ALLOW</option>
            <option value="REVIEW">REVIEW</option>
            <option value="BLOCK">BLOCK</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="filter-risk">Risk Level:</label>
          <select
            id="filter-risk"
            className="filter-select"
            value={filters.risk_level}
            onChange={handleRisk}
            aria-label="Filter events by risk tier"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="filter-behavior">Behavior:</label>
          <select
            id="filter-behavior"
            className="filter-select"
            value={filters.anomaly_detected}
            onChange={handleAnomaly}
            aria-label="Filter events by behavioral anomaly detection"
          >
            <option value="ALL">All Behaviors</option>
            <option value="true">Anomalous Only</option>
            <option value="false">Normal Only</option>
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <button
          type="button"
          onClick={resetFilters}
          aria-label="Reset all audit filters"
          style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', padding: '0.35rem 0.75rem', borderRadius: '6px', fontSize: '0.75rem', cursor: 'pointer' }}
        >
          Reset Filters
        </button>
      )}
    </div>
  );
}
