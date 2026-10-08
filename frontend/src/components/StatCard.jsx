import React from 'react';

export default function StatCard({ title, value, subtext, type = 'total' }) {
  return (
    <div className={`stat-card ${type}`}>
      <div className="stat-header">{title}</div>
      <div className="stat-value">{value}</div>
      {subtext && <div className="stat-subtext">{subtext}</div>}
    </div>
  );
}
