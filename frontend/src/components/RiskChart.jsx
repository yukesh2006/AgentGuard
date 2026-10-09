import React from 'react';

export default function RiskChart({ distribution = {}, total = 0 }) {
  const levels = [
    { key: 'LOW', label: 'Low (<25)', class: 'low', count: distribution.LOW || 0 },
    { key: 'MEDIUM', label: 'Medium (25-49)', class: 'medium', count: distribution.MEDIUM || 0 },
    { key: 'HIGH', label: 'High (50-74)', class: 'high', count: distribution.HIGH || 0 },
    { key: 'CRITICAL', label: 'Critical (≥75)', class: 'critical', count: distribution.CRITICAL || 0 },
  ];

  const safeTotal = total > 0 ? total : 1;

  return (
    <div className="dashboard-card" role="region" aria-label="Risk Assessment Threat Level Breakdown">
      <div className="card-title">
        <span>Risk Assessment Breakdown</span>
        <span className="card-subtitle">Multi-Factor Threat Levels</span>
      </div>
      <div className="chart-bars">
        {levels.map((lvl) => {
          const pct = Math.round((lvl.count / safeTotal) * 100);
          return (
            <div key={lvl.key} className="bar-row">
              <div className="bar-label-group">
                <span>{lvl.label}</span>
                <span>
                  {lvl.count} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({pct}%)</span>
                </span>
              </div>
              <div
                className="bar-track"
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin="0"
                aria-valuemax="100"
                aria-label={`${lvl.label}: ${lvl.count} events (${pct} percent)`}
              >
                <div
                  className={`bar-fill ${lvl.class}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
