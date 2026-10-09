import React from 'react';

export default function Header({ onRefresh, loading }) {
  return (
    <header className="dashboard-header" role="banner" aria-label="AgentGuard Application Header">
      <div className="brand-section">
        <div className="brand-logo-badge" aria-hidden="true">AG</div>
        <div className="brand-titles">
          <h1>
            AGENTGUARD
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#3b82f6', background: 'rgba(59,130,246,0.1)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(59,130,246,0.2)', marginLeft: '0.5rem' }}>
              SOC v0.3.0
            </span>
          </h1>
          <div className="subtitle">Context-Aware AI Intent Firewall & Security Gateway</div>
        </div>
      </div>

      <div className="header-controls">
        <div className="status-indicator" role="status" aria-live="polite" aria-label="System status: Online">
          <span className="pulse-dot" aria-hidden="true"></span>
          SYSTEM ONLINE
        </div>
        <button
          type="button"
          className="refresh-button"
          onClick={onRefresh}
          disabled={loading}
          aria-label="Refresh security dashboard metrics"
          title="Refresh dashboard metrics"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
          </svg>
          {loading ? 'SYNCING...' : 'REFRESH'}
        </button>
      </div>
    </header>
  );
}
