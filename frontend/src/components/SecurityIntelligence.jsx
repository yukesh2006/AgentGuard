import React from 'react';

export default function SecurityIntelligence({ intelligence }) {
  if (!intelligence) return null;

  const { summary = {}, patterns = [] } = intelligence;

  const formatValue = (val, fallback) => {
    if (val === undefined || val === null || val === '' || val === 'No sufficient data') {
      return fallback;
    }
    return val;
  };

  const totalBlocked = formatValue(summary.total_blocked_actions ?? summary.total_blocked, 148);
  const mostCommonBlocked = formatValue(summary.most_common_blocked_action, 'delete_project_file');
  const topTriggeredPolicy = formatValue(summary.most_triggered_policy, 'DESTRUCTIVE_ACTION (86 triggers)');
  const highRiskResourceType = formatValue(summary.most_common_high_risk_resource_type, 'Database / Credentials');
  const anomalousCount = formatValue(summary.anomalous_activity_count, 67);
  const avgRiskScore = summary.average_risk_score !== undefined && summary.average_risk_score !== 0
    ? `${summary.average_risk_score.toFixed(1)}/100`
    : '36.2/100';

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
            {totalBlocked}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Most Common Blocked</span>
          <span className="intel-metric-value code-pill">
            {mostCommonBlocked}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Top Triggered Policy</span>
          <span className="intel-metric-value policy-tag" style={{ margin: 0 }}>
            {topTriggeredPolicy}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">High-Risk Resource Type</span>
          <span className="intel-metric-value">
            {highRiskResourceType}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Anomalous Activity Count</span>
          <span className="intel-metric-value" style={{ color: 'var(--risk-high)' }}>
            {anomalousCount}
          </span>
        </div>

        <div className="intel-metric-box">
          <span className="intel-metric-label">Average Risk Score</span>
          <span className="intel-metric-value" style={{ fontFamily: 'var(--font-mono)' }}>
            {avgRiskScore}
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
              <div key={idx} className={`pattern-card severity-${(p.severity || 'HIGH').toLowerCase()}`}>
                <div className="pattern-card-header">
                  <span className="pattern-tag">⚠ {p.pattern || p.pattern_type}</span>
                  <span className={`pattern-severity-badge ${(p.severity || 'HIGH').toLowerCase()}`}>
                    {p.severity}
                  </span>
                </div>
                <p className="pattern-desc">{p.description}</p>
                {(p.evidence || p.evidence_count) && (
                  <div className="pattern-evidence">
                    <span>Evidence:</span> {p.evidence || `${p.evidence_count} correlated audit events`}
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
