import React from 'react';

export default function EventTable({ events = [], onSelectEvent }) {
  if (!events || events.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }} role="status">
        No audit events matching current criteria.
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
      onSelectEvent(evt);
    }
  };

  return (
    <div className="table-wrapper" role="region" aria-label="Security Interception Audit Events Table">
      <table className="events-table">
        <caption className="sr-only">Audit log of intercepted AI agent actions and policy decisions</caption>
        <thead>
          <tr>
            <th scope="col">Time</th>
            <th scope="col">Proposed Action</th>
            <th scope="col">Target Resource</th>
            <th scope="col">Verdict</th>
            <th scope="col">Risk Level</th>
            <th scope="col">Score</th>
            <th scope="col">Anomaly</th>
          </tr>
        </thead>
        <tbody>
          {events.map((evt) => (
            <tr
              key={evt.id}
              onClick={() => onSelectEvent(evt)}
              onKeyDown={(e) => handleKeyDown(e, evt)}
              tabIndex={0}
              role="button"
              aria-label={`View audit details for action ${evt.action} on ${evt.target_resource}, verdict ${evt.decision}`}
              title="Click or press Enter to view full security audit details"
            >
              <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                {formatTime(evt.timestamp)}
              </td>
              <td>
                <span className="code-pill">{evt.action}</span>
              </td>
              <td style={{ maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {evt.target_resource}
              </td>
              <td>
                <span className={`verdict-badge ${evt.decision.toLowerCase()}`}>
                  {evt.decision}
                </span>
              </td>
              <td style={{ fontWeight: 600, fontSize: '0.8rem' }}>
                {evt.risk_level}
              </td>
              <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                {typeof evt.risk_score === 'number' ? evt.risk_score.toFixed(1) : evt.risk_score}
              </td>
              <td>
                <span className={`anomaly-badge ${evt.anomaly_detected ? 'yes' : 'no'}`}>
                  {evt.anomaly_detected ? 'ANOMALY' : 'NORMAL'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
