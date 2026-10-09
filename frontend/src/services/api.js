/**
 * AgentGuard Frontend API Service.
 * Centralized HTTP client communicating with FastAPI backend, with seamless
 * autonomous fallback to client-side policy evaluation sandbox when static.
 */

import {
  DEMO_STATS,
  DEMO_POLICIES,
  DEMO_INTELLIGENCE,
  DEMO_EVENTS,
  simulateActionLocally,
} from './demoData';

const envApiBase = import.meta.env.VITE_API_BASE_URL;
const isLocalhost = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname === '[::1]'
);

const API_BASE = (envApiBase && envApiBase.trim() !== '')
  ? envApiBase.replace(/\/+$/, '')
  : (isLocalhost
    ? (typeof window !== 'undefined' && window.location.port === '5173' ? '' : 'http://127.0.0.1:8000')
    : '');

// Mutable in-memory state for standalone / demo sandbox mode
let runtimeDemoEvents = [...DEMO_EVENTS];
let runtimeDemoStats = {
  ...DEMO_STATS,
  risk_distribution: { ...DEMO_STATS.risk_distribution },
  decision_distribution: { ...DEMO_STATS.decision_distribution },
};
let runtimeDemoPolicies = { ...DEMO_POLICIES };

/**
 * Robust fetch wrapper that gracefully detects SPA HTML fallback or network errors.
 */
async function safeFetchJson(url, options = {}) {
  // If no backend configured and not on localhost, directly utilize standalone sandbox
  if (!API_BASE && !isLocalhost) {
    return null;
  }

  try {
    const res = await fetch(url, options);
    // If Firebase Hosting returns index.html for unknown backend route, content-type is text/html
    const contentType = res.headers.get('content-type') || '';
    if (contentType.includes('text/html')) {
      return null;
    }
    if (!res.ok) {
      return null;
    }
    return await res.json();
  } catch (err) {
    return null;
  }
}

/**
 * Fetch dashboard overview statistics.
 */
export async function getAuditStats() {
  const data = await safeFetchJson(`${API_BASE}/audit/stats`);
  if (data && typeof data.total_events === 'number') {
    return data;
  }
  return { ...runtimeDemoStats };
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
  const data = await safeFetchJson(url);
  if (data && Array.isArray(data)) {
    return data;
  }

  // Filter in-memory events
  let filtered = [...runtimeDemoEvents];
  if (filters.decision && filters.decision !== 'ALL') {
    filtered = filtered.filter(e => e.decision === filters.decision);
  }
  if (filters.risk_level && filters.risk_level !== 'ALL') {
    filtered = filtered.filter(e => e.risk_level === filters.risk_level);
  }
  if (filters.anomaly_detected !== undefined && filters.anomaly_detected !== 'ALL') {
    const wantAnomaly = filters.anomaly_detected === 'true' || filters.anomaly_detected === true;
    filtered = filtered.filter(e => !!e.anomaly_detected === wantAnomaly);
  }

  const limit = filters.limit ? parseInt(filters.limit, 10) : 50;
  return filtered.slice(0, limit);
}

/**
 * Fetch complete audit record details for a specific event.
 */
export async function getAuditEvent(eventId) {
  const data = await safeFetchJson(`${API_BASE}/audit/events/${eventId}`);
  if (data) {
    return data;
  }
  const match = runtimeDemoEvents.find(e => String(e.id) === String(eventId) || e.interception_id === eventId);
  return match || runtimeDemoEvents[0] || null;
}

/**
 * Fetch triggered policy frequency analytics.
 */
export async function getPolicyStats() {
  const data = await safeFetchJson(`${API_BASE}/audit/policies`);
  if (data && typeof data === 'object') {
    return data;
  }
  return { ...runtimeDemoPolicies };
}

/**
 * Intercept an AI agent's proposed action and simulate execution.
 */
export async function interceptAction(payload, includeTrace = true) {
  const url = `${API_BASE}/intercept${includeTrace ? '?include_trace=true' : ''}`;

  if (API_BASE || isLocalhost) {
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      const contentType = res.headers.get('content-type') || '';
      if (!contentType.includes('text/html') && res.ok) {
        return await res.json();
      }
    } catch (err) {
      // Fall through to client simulation
    }
  }

  // Client-side fallback simulation
  const result = simulateActionLocally(payload);

  // Dynamically record into runtime events for live UI reactivity
  const goal = payload.user_goal || payload.user_request || '';
  const action = payload.agent_action || payload.action || 'read_project_file';
  const resource = payload.target_resource || payload.resource || 'unknown';
  const destination = payload.destination || 'local';

  const newEvent = {
    id: runtimeDemoEvents.length + 313,
    interception_id: result.interception_id,
    timestamp: result.timestamp,
    user_goal: goal,
    action: action,
    target_resource: resource,
    destination: destination,
    decision: result.decision,
    risk_score: result.risk_score,
    risk_level: result.risk_level,
    explanation: result.reason || result.message,
    triggered_policies: result.triggered_policies || [],
    simulation_status: result.simulation_status,
    execution_permitted: result.execution_permitted,
    review_status: result.review_status,
    anomaly_detected: result.anomaly_detected,
    intent_similarity: result.decision_trace?.intent_analysis?.intent_action_similarity || 0.42,
    decision_trace: result.decision_trace,
  };

  runtimeDemoEvents = [newEvent, ...runtimeDemoEvents];

  // Update stats
  runtimeDemoStats.total_events += 1;
  if (result.decision === 'ALLOW') runtimeDemoStats.allowed += 1;
  else if (result.decision === 'REVIEW') runtimeDemoStats.review += 1;
  else if (result.decision === 'BLOCK') runtimeDemoStats.blocked += 1;

  if (result.risk_level === 'HIGH') runtimeDemoStats.high_risk_events += 1;
  if (result.risk_level === 'CRITICAL') runtimeDemoStats.critical_events += 1;
  if (result.anomaly_detected) runtimeDemoStats.anomalous_events += 1;

  if (runtimeDemoStats.risk_distribution[result.risk_level] !== undefined) {
    runtimeDemoStats.risk_distribution[result.risk_level] += 1;
  }
  if (runtimeDemoStats.decision_distribution[result.decision] !== undefined) {
    runtimeDemoStats.decision_distribution[result.decision] += 1;
  }

  // Update policies
  if (result.triggered_policies) {
    for (const pol of result.triggered_policies) {
      runtimeDemoPolicies[pol] = (runtimeDemoPolicies[pol] || 0) + 1;
    }
  }

  return result;
}

/**
 * Fetch explainable AI decision trace for a specific interception ID.
 */
export async function getDecisionTrace(interceptionId) {
  const data = await safeFetchJson(`${API_BASE}/explain/${interceptionId}`);
  if (data) {
    return data;
  }

  const match = runtimeDemoEvents.find(e => e.interception_id === interceptionId);
  if (match && match.decision_trace) {
    return {
      interception_id: match.interception_id,
      decision_trace: match.decision_trace,
    };
  }

  const sim = simulateActionLocally({
    user_goal: match ? match.user_goal : 'Project audit inspection',
    action: match ? match.action : 'read_project_file',
    target_resource: match ? match.target_resource : 'data.csv',
  });

  return {
    interception_id: interceptionId,
    decision_trace: sim.decision_trace,
  };
}

/**
 * Fetch proactive security intelligence analytics and threat patterns.
 */
export async function getSecurityIntelligence() {
  const data = await safeFetchJson(`${API_BASE}/security/intelligence`);
  if (data && typeof data === 'object') {
    return data;
  }
  return { ...DEMO_INTELLIGENCE };
}
