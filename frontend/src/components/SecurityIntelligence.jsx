import React from 'react';

export default function SecurityIntelligence({ intelligence }) {
  if (!intelligence) return null;

  const { summary = {}, patterns = [] } = intelligence;

  const formatValue = (val) => {
    if (val === undefined || val === null || val === '') return 'No sufficient data';
    return val;
  };

  return (
    <div className="dashboard-card security-intelligence-card" style={{ marginBottom: '2rem' }}>
      <div className="card-title">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span style={{ display: 'inline-block', width: '10px', height: '10px', borderRadius: '50%', background: 'var(--accent-cyan)' }}></span>
          <span>Security Intelligence & Threat Patterns</span>
        </div>
        <span className="card-subtitle">Proactive Multi-Event Behavioral Correlation</span>
      </div>

      {/* Intelligence Summary Row */}
      <div className="intel-metrics-grid">
        <div className="intel-metric-box">
          <span className="intel-metric-label">Total Blocked Actions</span>
          <span className="intel-metric-value" style={{ color: 'var(--color-block)' }}>
            {formatValue(summary.total_blocked_actions)}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Most Common Blocked</span>
          <span className="intel-metric-value code-pill">
            {formatValue(summary.most_common_blocked_action)}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Top Triggered Policy</span>
          <span className="intel-metric-value policy-tag" style={{ margin: 0 }}>
            {formatValue(summary.most_triggered_policy)}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">High-Risk Resource Type</span>
          <span className="intel-metric-value">
            {formatValue(summary.most_common_high_risk_resource_type)}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Anomalous Activity Count</span>
          <span className="intel-metric-value" style={{ color: 'var(--risk-high)' }}>
            {formatValue(summary.anomalous_activity_count)}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Average Risk Score</span>
          <span className="intel-metric-value" style={{ fontFamily: 'var(--font-mono)' }}>
            {summary.average_risk_score !== undefined ? `${summary.average_risk_score.toFixed(1)}/100` : 'No sufficient data'}
          </span>
        </div>
      </div>

      {/* Threat Pattern Detection Section */}
      <div className="threat-patterns-section" style={{ marginTop: '1.25rem' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
          Correlated Threat Patterns
        </div>

        {patterns && patterns.length > 0 ? (
          <div className="pattern-cards-grid">
            {patterns.map((p, idx) => (
              <div key={idx} className={`pattern-card severity-${p.severity.toLowerCase()}`}>
                <div className="pattern-card-header">
                  <span className="pattern-tag">⚠ {p.pattern}</span>
                  <span className={`pattern-severity-badge ${p.severity.toLowerCase()}`}>
                    {p.severity}
                  </span>
                </div>
                <p className="pattern-desc">{p.description}</p>
                {p.evidence && (
                  <div className="pattern-evidence">
                    <span>Evidence:</span> {p.evidence}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="no-patterns-badge">
            <span style={{ color: 'var(--color-allow)', marginRight: '0.5rem', fontWeight: 'bold' }}>✓</span>
            NO ACTIVE THREAT PATTERNS DETECTED — Historical audit log shows normal behavioral compliance.
          </div>
        )}
      </div>
    </div>
  );
}
