import React from 'react';

export default function EventDetails({ event, onClose }) {
  if (!event) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
              <span className={`verdict-badge ${event.decision.toLowerCase()}`}>
                {event.decision}
              </span>
              <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-mono)' }}>
                {event.interception_id}
              </h2>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Recorded at: {new Date(event.timestamp).toLocaleString()}
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            &times;
          </button>
        </div>

        <div className="detail-grid">
          <div className="detail-group full">
            <span className="detail-label">User Goal / Stated Intent</span>
            <div className="detail-value" style={{ background: 'var(--bg-primary)', padding: '0.6rem 0.85rem', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
              "{event.user_goal}"
            </div>
          </div>

          <div className="detail-group">
            <span className="detail-label">Requested Action</span>
            <div className="detail-value">
              <span className="code-pill">{event.action}</span>
            </div>
          </div>

          <div className="detail-group">
            <span className="detail-label">Target Resource</span>
            <div className="detail-value" style={{ fontFamily: 'var(--font-mono)' }}>
              {event.target_resource}
            </div>
          </div>

          {event.destination && (
            <div className="detail-group full">
              <span className="detail-label">External Destination</span>
              <div className="detail-value" style={{ fontFamily: 'var(--font-mono)', color: '#fca5a5' }}>
                {event.destination}
              </div>
            </div>
          )}

          <div className="detail-group">
            <span className="detail-label">Risk Assessment</span>
            <div className="detail-value" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontWeight: 800, fontSize: '1.1rem', fontFamily: 'var(--font-mono)' }}>
                {event.risk_score.toFixed(1)}/100
              </span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                ({event.risk_level})
              </span>
            </div>
          </div>

          <div className="detail-group">
            <span className="detail-label">Behavioral Anomaly</span>
            <div className="detail-value">
              <span className={`anomaly-badge ${event.anomaly_detected ? 'yes' : 'no'}`}>
                {event.anomaly_detected ? 'Anomaly Detected' : 'Normal Sequence'}
              </span>
            </div>
          </div>

          <div className="detail-group full">
            <span className="detail-label">Triggered Security Policies</span>
            <div className="policy-tags">
              {event.triggered_policies && event.triggered_policies.length > 0 ? (
                event.triggered_policies.map((pol, idx) => (
                  <span key={idx} className="policy-tag">
                    {pol}
                  </span>
                ))
              ) : (
                <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>None</span>
              )}
            </div>
          </div>

          <div className="detail-group">
            <span className="detail-label">Simulation Status</span>
            <div className="detail-value" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
              {event.simulation_status}
            </div>
          </div>

          <div className="detail-group">
            <span className="detail-label">Execution Permitted?</span>
            <div className="detail-value">
              <span style={{ fontWeight: 700, color: event.execution_permitted ? 'var(--color-allow)' : 'var(--color-block)' }}>
                {event.execution_permitted ? 'YES (Simulated)' : 'NO (Halted / Denied)'}
              </span>
            </div>
          </div>

          <div className="detail-group full">
            <span className="detail-label">Policy Reason & Explanation</span>
            <div className="detail-value" style={{ background: 'var(--bg-primary)', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid var(--border-subtle)', lineHeight: 1.6 }}>
              {event.explanation}
            </div>
          </div>

          {event.simulation_output && (
            <div className="detail-group full">
              <span className="detail-label">Safe Simulation Output Payload</span>
              <pre style={{ background: 'var(--bg-primary)', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid var(--border-subtle)', fontSize: '0.75rem', fontFamily: 'var(--font-mono)', overflowX: 'auto', color: '#93c5fd' }}>
                {JSON.stringify(event.simulation_output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
