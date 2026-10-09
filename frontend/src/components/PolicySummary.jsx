import React from 'react';

export default function PolicySummary({ policies = {} }) {
  const policyEntries = Object.entries(policies);

  return (
    <div className="dashboard-card" role="region" aria-label="Top Triggered Security Policies">
      <div className="card-title">
        <span>Top Triggered Policies</span>
        <span className="card-subtitle">Enforcement Rule Triggers</span>
      </div>

      {policyEntries.length === 0 ? (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '1rem 0' }} role="status">
          No policy triggers recorded yet.
        </div>
      ) : (
        <div className="policy-list" role="list" aria-label="Triggered Policies Ranking">
          {policyEntries.slice(0, 6).map(([name, count]) => (
            <div key={name} className="policy-item" role="listitem">
              <span className="policy-name">{name}</span>
              <span className="policy-count" aria-label={`${count} triggers`}>{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
