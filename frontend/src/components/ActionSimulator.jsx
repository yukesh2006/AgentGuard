import React, { useState } from 'react';
import { interceptAction } from '../services/api';
import { simulateActionLocally } from '../services/demoData';

const PRESETS = [
  {
    name: '1. Aligned Report Read',
    goal: 'Prepare my monthly project report.',
    action: 'read_project_file',
    resource: 'project_data.csv',
    dest: '',
  },
  {
    name: '2. Destructive Mismatch',
    goal: 'Prepare my monthly project report.',
    action: 'delete_project_file',
    resource: 'project_data.csv',
    dest: '',
  },
  {
    name: '3. External Exfiltration',
    goal: 'Prepare my monthly project report.',
    action: 'upload_external',
    resource: 'unknown_external_server',
    dest: 'https://unknown-server.com/upload',
  },
  {
    name: '4. Sensitive Credentials',
    goal: 'Check my project configuration.',
    action: 'read_project_file',
    resource: 'credentials.txt',
    dest: '',
  },
  {
    name: '5. Suspicious Shell Command',
    goal: 'Prepare my monthly project report.',
    action: 'execute_command',
    resource: 'bash',
    dest: '',
  },
  {
    name: '6. Legitimate Email',
    goal: 'Send the completed report to my professor.',
    action: 'send_email',
    resource: 'professor@university.edu',
    dest: '',
  },
];

export default function ActionSimulator({ onInterceptionComplete }) {
  const [goal, setGoal] = useState(PRESETS[0].goal);
  const [action, setAction] = useState(PRESETS[0].action);
  const [resource, setResource] = useState(PRESETS[0].resource);
  const [destination, setDestination] = useState(PRESETS[0].dest);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const applyPreset = (preset) => {
    setGoal(preset.goal);
    setAction(preset.action);
    setResource(preset.resource);
    setDestination(preset.dest);
    setResult(null);
    setError(null);
  };

  const handleIntercept = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (loading) return;

    setLoading(true);
    setError(null);
    try {
      const payload = {
        user_goal: goal,
        user_request: goal,
        agent_action: action,
        action: action,
        target_resource: resource,
        resource: resource,
        destination: destination || undefined,
      };

      let response;
      try {
        response = await interceptAction(payload);
      } catch (apiErr) {
        console.warn('[ActionSimulator] Remote intercept error, using local simulation:', apiErr);
        response = simulateActionLocally(payload);
      }

      if (!response || !response.decision) {
        response = simulateActionLocally(payload);
      }

      setResult(response);
      if (onInterceptionComplete) {
        try {
          onInterceptionComplete();
        } catch (_) {}
      }
    } catch (err) {
      console.error('[ActionSimulator] Critical interception error:', err);
      const fallback = simulateActionLocally({
        user_goal: goal,
        action: action,
        target_resource: resource,
        destination: destination,
      });
      setResult(fallback);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulator-section">
      <div className="card-title">
        <span>Agent Action Simulator</span>
        <span className="card-subtitle">Live Interception Sandbox (Safe Simulation Only)</span>
      </div>

      <div style={{ marginBottom: '0.75rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
        Select a demonstration preset or enter custom agent action parameters:
      </div>

      <div className="preset-pills">
        {PRESETS.map((p, idx) => (
          <button
            key={idx}
            type="button"
            className="preset-pill"
            onClick={() => applyPreset(p)}
          >
            {p.name}
          </button>
        ))}
      </div>

      <form onSubmit={handleIntercept}>
        <div className="simulator-form">
          <div className="form-group">
            <label>User Goal / Task Intent</label>
            <input
              type="text"
              className="form-input"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="e.g. Prepare monthly project report"
              required
            />
          </div>

          <div className="form-group">
            <label>Proposed Agent Action</label>
            <select
              className="form-select"
              value={action}
              onChange={(e) => setAction(e.target.value)}
            >
              <option value="read_project_file">read_project_file</option>
              <option value="delete_project_file">delete_project_file</option>
              <option value="upload_external">upload_external</option>
              <option value="execute_command">execute_command</option>
              <option value="send_email">send_email</option>
              <option value="write_file">write_file</option>
              <option value="query_database">query_database</option>
              <option value="list_directory">list_directory</option>
              <option value="read_credentials_file">read_credentials_file</option>
            </select>
          </div>

          <div className="form-group">
            <label>Target Resource</label>
            <input
              type="text"
              className="form-input"
              value={resource}
              onChange={(e) => setResource(e.target.value)}
              placeholder="e.g. project_data.csv"
              required
            />
          </div>

          <div className="form-group">
            <label>Destination (Optional)</label>
            <input
              type="text"
              className="form-input"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="e.g. https://server.com/upload"
            />
          </div>
        </div>

        <button
          type="button"
          onClick={handleIntercept}
          className="btn-intercept"
          id="btn-analyze-action"
          disabled={loading || !goal.trim() || !resource.trim()}
        >
          {loading ? 'INTERCEPTING & ANALYZING...' : 'ANALYZE ACTION'}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: '1rem', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', padding: '0.75rem', borderRadius: '8px', color: '#fca5a5', fontSize: '0.82rem' }}>
          Error: {error}
        </div>
      )}

      {result && (
        <div className="sim-result-banner" id="sim-result-banner">
          <div className="sim-result-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span className={`verdict-badge ${(result.decision || 'allow').toLowerCase()}`}>
                {result.decision || 'ALLOW'}
              </span>
              <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '0.85rem' }}>
                Risk: {typeof result.risk_score === 'number' ? result.risk_score.toFixed(1) : (Number(result.risk_score) || 0).toFixed(1)}/100 ({result.risk_level || 'LOW'})
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              {result.interception_id}
            </div>
          </div>

          <div style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
            {result.reason || result.message}
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center', fontSize: '0.78rem', paddingTop: '0.25rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Simulation: </span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{result.simulation_status || 'SIMULATED_SUCCESS'}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Execution Permitted: </span>
              <strong style={{ color: result.execution_permitted ? 'var(--color-allow)' : 'var(--color-block)' }}>
                {result.execution_permitted ? 'YES (Simulated)' : 'NO (Halted)'}
              </strong>
            </div>
            {result.triggered_policies && result.triggered_policies.length > 0 && (
              <div style={{ display: 'flex', gap: '0.3rem', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-muted)' }}>Policies: </span>
                {result.triggered_policies.map((p, i) => (
                  <span key={i} className="policy-tag" style={{ fontSize: '0.7rem' }}>
                    {p}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
