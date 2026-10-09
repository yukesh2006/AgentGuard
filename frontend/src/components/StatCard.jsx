import React from 'react';

export default function StatCard({ title, value, subtext, type = 'total' }) {
  return (
    <article
      className={`stat-card ${type}`}
      aria-label={`${title}: ${value}. ${subtext || ''}`}
    >
      <h2 className="stat-header" style={{ fontSize: '0.8rem', fontWeight: 600 }}>{title}</h2>
      <div className="stat-value" aria-live="polite">{value}</div>
      {subtext && <div className="stat-subtext">{subtext}</div>}
    </article>
  );
}
