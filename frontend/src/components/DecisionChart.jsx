import React from 'react';

export default function DecisionChart({ distribution = {}, total = 0 }) {
  const verdicts = [
    { key: 'ALLOW', label: 'ALLOW (Permitted)', class: 'allow', count: distribution.ALLOW || 0 },
    { key: 'REVIEW', label: 'REVIEW (HITL Queue)', class: 'review', count: distribution.REVIEW || 0 },
    { key: 'BLOCK', label: 'BLOCK (Denied)', class: 'block', count: distribution.BLOCK || 0 },
  ];

  const safeTotal = total > 0 ? total : 1;

  return (
    <div className="dashboard-card" role="region" aria-label="Policy Verdict Distribution Breakdown">
      <div className="card-title">
        <span>Policy Verdict Distribution</span>
        <span className="card-subtitle">Enforced Gateway Actions</span>
      </div>
      <div className="chart-bars">
        {verdicts.map((v) => {
          const pct = Math.round((v.count / safeTotal) * 100);
          return (
            <div key={v.key} className="bar-row">
              <div className="bar-label-group">
                <span>{v.label}</span>
                <span>
                  {v.count} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({pct}%)</span>
                </span>
              </div>
              <div
                className="bar-track"
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin="0"
                aria-valuemax="100"
                aria-label={`${v.label}: ${v.count} events (${pct} percent)`}
              >
                <div
                  className={`bar-fill ${v.class}`}
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
