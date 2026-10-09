/**
 * AgentGuard Frontend API Service.
 * Centralized HTTP client communicating with FastAPI backend.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : '';

/**
 * Fetch dashboard overview statistics.
 */
export async function getAuditStats() {
  const res = await fetch(`${API_BASE}/audit/stats`);
  if (!res.ok) {
    throw new Error(`Failed to fetch stats: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch persistent audit events with optional query filters.
 */
export async function getAuditEvents(filters = {}) {
  const params = new URLSearchParams();
  if (filters.limit) params.append('limit', filters.limit);
  if (filters.offset) params.append('offset', filters.offset);
  if (filters.decision && filters.decision !== 'ALL') params.append('decision', filters.decision);
  if (filters.risk_level && filters.risk_level !== 'ALL') params.append('risk_level', filters.risk_level);
  if (filters.anomaly_detected !== undefined && filters.anomaly_detected !== 'ALL') {
    params.append('anomaly_detected', filters.anomaly_detected === 'true' || filters.anomaly_detected === true);
  }

  const url = `${API_BASE}/audit/events?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch events: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch complete audit record details for a specific event.
 */
export async function getAuditEvent(eventId) {
  const res = await fetch(`${API_BASE}/audit/events/${eventId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch event detail: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch triggered policy frequency analytics.
 */
export async function getPolicyStats() {
  const res = await fetch(`${API_BASE}/audit/policies`);
  if (!res.ok) {
    throw new Error(`Failed to fetch policy stats: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Intercept an AI agent's proposed action and simulate execution.
 */
export async function interceptAction(payload, includeTrace = true) {
  const url = `${API_BASE}/intercept${includeTrace ? '?include_trace=true' : ''}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Interception failed: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch explainable AI decision trace for a specific interception ID.
 */
export async function getDecisionTrace(interceptionId) {
  const res = await fetch(`${API_BASE}/explain/${interceptionId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch decision trace: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch proactive security intelligence analytics and threat patterns.
 */
export async function getSecurityIntelligence() {
  const res = await fetch(`${API_BASE}/security/intelligence`);
  if (!res.ok) {
    throw new Error(`Failed to fetch security intelligence: ${res.statusText}`);
  }
  return res.json();
}
