import React from 'react';

export default function PolicySummary({ policies = {} }) {
  const policyEntries = Object.entries(policies);

  return (
    <div className="dashboard-card">
      <div className="card-title">
        <span>Top Triggered Policies</span>
        <span className="card-subtitle">Enforcement Rule Triggers</span>
      </div>

      {policyEntries.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '1rem 0' }}>
          No policy triggers recorded yet.
        </div>
      ) : (
        <div className="policy-list">
          {policyEntries.slice(0, 6).map(([name, count]) => (
            <div key={name} className="policy-item">
              <span className="policy-name">{name}</span>
              <span className="policy-count">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
