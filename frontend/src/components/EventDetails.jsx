import React, { useState, useEffect } from 'react';
import { getDecisionTrace } from '../services/api';

export default function EventDetails({ event, onClose }) {
  const [trace, setTrace] = useState(event?.decision_trace || null);
  const [loadingTrace, setLoadingTrace] = useState(!event?.decision_trace);
  const [traceError, setTraceError] = useState(null);

  useEffect(() => {
    if (event?.decision_trace) {
      setTrace(event.decision_trace);
      setLoadingTrace(false);
      return;
    }

    if (event?.interception_id) {
      let isMounted = true;
      setLoadingTrace(true);
      getDecisionTrace(event.interception_id)
        .then((data) => {
          if (isMounted) {
            setTrace(data.decision_trace);
            setLoadingTrace(false);
          }
        })
        .catch((err) => {
          if (isMounted) {
            console.warn('Could not fetch decision trace:', err);
            setTraceError('Trace reconstruction unavailable from historical logs.');
            setLoadingTrace(false);
          }
        });
      return () => {
        isMounted = false;
      };
    }
  }, [event]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!event) return null;

  const decision = trace?.final_decision || event.decision;
  const riskScore = trace ? trace.risk_score : event.risk_score;
  const riskLevel = trace ? trace.risk_level : event.risk_level;
  const confidence = trace?.decision_confidence;
  const reasoningChain = trace?.reasoning_chain || [];
  const riskFactors = trace?.risk_factors || [];

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="modal-card trace-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-trace-title"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
              <span className={`verdict-badge ${decision.toLowerCase()}`}>
                {decision}
              </span>
              <h2 id="modal-trace-title" style={{ fontSize: '1.25rem', fontFamily: 'var(--font-mono)' }}>
                {event.interception_id}
              </h2>
              {confidence && (
                <span className={`confidence-badge confidence-${confidence.confidence_level.toLowerCase()}`} title={confidence.rationale}>
                  CONFIDENCE: {confidence.confidence_level}
                </span>
              )}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Recorded at: {new Date(event.timestamp).toLocaleString()}
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close security details dialog" type="button">
            &times;
          </button>
        </div>

        {/* Confidence Disclaimer */}
        {confidence && (
          <div className="confidence-disclaimer">
            <span>ℹ Decision Confidence: <strong>{confidence.confidence_level}</strong></span> — {confidence.rationale}
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              {confidence.disclaimer}
            </div>
          </div>
        )}

        {/* Section 1: Plain-English Security Explanation Card */}
        <div className={`explanation-card decision-${decision.toLowerCase()}`}>
          <div className="explanation-title">
            🛡 Why AgentGuard Took This Action
          </div>
          <div className="explanation-body">
            {trace?.detailed_explanation || trace?.decision_reason || event.explanation}
          </div>
        </div>

        {/* Section 2: Visual Decision Reasoning Pipeline */}
        <div className="pipeline-section">
          <div className="section-title">
            <span>Decision Reasoning Chain</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>7-Stage Intent Firewall Pipeline</span>
          </div>

          {loadingTrace ? (
            <div style={{ padding: '1rem', color: 'var(--text-muted)', textAlign: 'center' }}>
              Reconstructing evidence trace...
            </div>
          ) : reasoningChain.length > 0 ? (
            <div className="pipeline-steps">
              {reasoningChain.map((step, idx) => (
                <div key={idx} className="pipeline-step-wrapper">
                  <div className={`pipeline-node status-${step.status.toLowerCase()}`}>
                    <div className="node-stage">{step.stage}</div>
                    <div className="node-status">{step.status}</div>
                    <div className="node-summary">{step.summary}</div>
                  </div>
                  {idx < reasoningChain.length - 1 && (
                    <div className="pipeline-arrow">↓</div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              {traceError || 'Standard evaluation sequence.'}
            </div>
          )}
        </div>

        {/* Section 3: Why This Risk Score? */}
        <div className="risk-factors-breakdown-card">
          <div className="section-title">
            <span>Why This Risk Score?</span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-primary)' }}>
              Assessed Risk: {riskScore.toFixed(1)}/100 ({riskLevel})
            </span>
          </div>

          {riskFactors.length > 0 ? (
            <div className="risk-factors-list">
              <div className="risk-factors-header">
                <span>Active Risk Contributor</span>
                <span>Severity</span>
                <span>Evidence / Assessment</span>
                <span>Impact</span>
              </div>
              {riskFactors.map((rf, idx) => (
                <div key={idx} className="risk-factor-row">
                  <span className="factor-name code-pill">{rf.factor}</span>
                  <span className={`factor-severity severity-${rf.severity.toLowerCase()}`}>
                    {rf.severity}
                  </span>
                  <span className="factor-evidence">{rf.evidence}</span>
                  <span className="factor-impact">+{rf.contribution}</span>
                </div>
              ))}
              <div className="risk-factors-footer">
                <span>Computed Composite Score</span>
                <span className="score-sum">
                  {riskScore.toFixed(1)} / 100 {riskScore >= 100 ? '(Engine Cap Applied)' : ''}
                </span>
              </div>
            </div>
          ) : (
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Baseline normal activity — no elevated risk factors triggered. Base risk score: {riskScore.toFixed(1)}/100.
            </div>
          )}
        </div>

        {/* Section 4: Event Context & Safe Simulation Details */}
        <div className="detail-grid" style={{ marginTop: '1.5rem' }}>
          <div className="detail-group full">
            <span className="detail-label">User Goal / Stated Intent</span>
            <div className="detail-value user-goal-box">
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
            <span className="detail-label">Behavioral Anomaly</span>
            <div className="detail-value">
              <span className={`anomaly-badge ${event.anomaly_detected ? 'yes' : 'no'}`}>
                {event.anomaly_detected ? 'Anomaly Detected' : 'Normal Sequence'}
              </span>
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

          {event.simulation_output && (
            <div className="detail-group full">
              <span className="detail-label">Safe Simulation Output Payload</span>
              <pre className="sim-output-pre">
                {JSON.stringify(event.simulation_output, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
