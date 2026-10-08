import React from 'react';

export default function SecurityTimeline({ events = [], onSelectEvent }) {
  const recentEvents = events.slice(0, 7);

  if (!recentEvents || recentEvents.length === 0) {
    return (
      <div className="dashboard-card">
        <div className="card-title">
          <span>Security Activity Timeline</span>
          <span className="card-subtitle">Real-Time Ingestion Feed</span>
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '1rem 0' }}>
          No recent security events recorded.
        </div>
      </div>
    );
  }

  const formatTime = (ts) => {
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts;
    }
  };

  return (
    <div className="dashboard-card">
      <div className="card-title">
        <span>Security Activity Timeline</span>
        <span className="card-subtitle">Real-Time Ingestion Feed</span>
      </div>

      <div className="timeline-list">
        {recentEvents.map((evt) => (
          <div
            key={evt.id}
            className="timeline-item"
            onClick={() => onSelectEvent && onSelectEvent(evt)}
            style={{ cursor: 'pointer' }}
            title="Click to view full record"
          >
            <div className="timeline-desc">
              <span className="timeline-time">{formatTime(evt.timestamp)}</span>
              <span>AI Agent requested <strong style={{ color: '#93c5fd' }}>{evt.action}</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>&rarr;</span>
              <span className={`verdict-badge ${evt.decision.toLowerCase()}`}>
                {evt.decision}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
