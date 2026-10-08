import React from 'react';

export default function EventTable({ events = [], onSelectEvent }) {
  if (!events || events.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
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

  return (
    <div className="table-wrapper">
      <table className="events-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Proposed Action</th>
            <th>Target Resource</th>
            <th>Verdict</th>
            <th>Risk Level</th>
            <th>Score</th>
            <th>Anomaly</th>
          </tr>
        </thead>
        <tbody>
          {events.map((evt) => (
            <tr key={evt.id} onClick={() => onSelectEvent(evt)} title="Click to view full security audit details">
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
                {evt.risk_score.toFixed(1)}
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
