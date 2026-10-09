import React from 'react';

export default function SecurityTimeline({ events = [], onSelectEvent }) {
  const recentEvents = events.slice(0, 7);

  if (!recentEvents || recentEvents.length === 0) {
    return (
      <div className="dashboard-card" role="region" aria-label="Security Activity Timeline Feed">
        <div className="card-title">
          <span>Security Activity Timeline</span>
          <span className="card-subtitle">Real-Time Ingestion Feed</span>
        </div>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '1rem 0' }} role="status">
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

  const handleKeyDown = (e, evt) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (onSelectEvent) onSelectEvent(evt);
    }
  };

  return (
    <div className="dashboard-card" role="region" aria-label="Security Activity Timeline Feed">
      <div className="card-title">
        <span>Security Activity Timeline</span>
        <span className="card-subtitle">Real-Time Ingestion Feed</span>
      </div>

      <div className="timeline-list" role="feed" aria-label="Recent Interceptions Feed">
        {recentEvents.map((evt) => (
          <div
            key={evt.id}
            className="timeline-item"
            onClick={() => onSelectEvent && onSelectEvent(evt)}
            onKeyDown={(e) => handleKeyDown(e, evt)}
            tabIndex={0}
            role="button"
            aria-label={`Security event at ${formatTime(evt.timestamp)}: ${evt.action}, verdict ${evt.decision}`}
            style={{ cursor: 'pointer' }}
            title="Click or press Enter to view full record"
          >
            <div className="timeline-desc">
              <span className="timeline-time">{formatTime(evt.timestamp)}</span>
              <span>AI Agent requested <strong style={{ color: '#93c5fd' }}>{evt.action}</strong></span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }} aria-hidden="true">&rarr;</span>
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
