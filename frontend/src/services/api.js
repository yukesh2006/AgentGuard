/**
 * AgentGuard Frontend API Service.
 * Centralized HTTP client communicating with FastAPI backend.
 * Features automatic failover to client-side demonstration sandbox
 * when running on static hosting without a live backend connection.
 */

import {
  DEMO_STATS,
  DEMO_EVENTS,
  DEMO_POLICIES,
  DEMO_INTELLIGENCE,
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

// Local fallback store for dynamic additions during simulation
let activeDemoEvents = [...DEMO_EVENTS];
let activeDemoStats = { ...DEMO_STATS };

/**
 * Robust JSON fetcher that guards against HTML responses from SPA rewrites.
 */
async function safeFetchJson(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('text/html')) {
    throw new Error(`Endpoint returned HTML: ${url}`);
  }
  return res.json();
}

/**
 * Fetch dashboard overview statistics.
 */
export async function getAuditStats() {
  try {
    return await safeFetchJson(`${API_BASE}/audit/stats`);
  } catch (err) {
    console.info('[AgentGuard] Live backend unreachable; using simulation sandbox stats.');
    return activeDemoStats;
  }
}

/**
 * Fetch persistent audit events with optional query filters.
 */
export async function getAuditEvents(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);
    if (filters.decision && filters.decision !== 'ALL') params.append('decision', filters.decision);
    if (filters.risk_level && filters.risk_level !== 'ALL') params.append('risk_level', filters.risk_level);
    if (filters.anomaly_detected !== undefined && filters.anomaly_detected !== 'ALL') {
      params.append('anomaly_detected', filters.anomaly_detected === 'true' || filters.anomaly_detected === true);
    }
    const url = `${API_BASE}/audit/events?${params.toString()}`;
    return await safeFetchJson(url);
  } catch (err) {
    console.info('[AgentGuard] Live backend unreachable; using simulation sandbox events.');
    let filtered = [...activeDemoEvents];
    if (filters.decision && filters.decision !== 'ALL') {
      filtered = filtered.filter((e) => e.decision === filters.decision);
    }
    if (filters.risk_level && filters.risk_level !== 'ALL') {
      filtered = filtered.filter((e) => e.risk_level === filters.risk_level);
    }
    if (filters.anomaly_detected !== undefined && filters.anomaly_detected !== 'ALL') {
      const wantAnomaly = filters.anomaly_detected === 'true' || filters.anomaly_detected === true;
      filtered = filtered.filter((e) => Boolean(e.anomaly_detected) === wantAnomaly);
    }
    return filtered;
  }
}

/**
 * Fetch complete audit record details for a specific event.
 */
export async function getAuditEvent(eventId) {
  try {
    return await safeFetchJson(`${API_BASE}/audit/events/${eventId}`);
  } catch (err) {
    const found = activeDemoEvents.find((e) => String(e.id) === String(eventId) || e.interception_id === eventId);
    if (found) return found;
    return activeDemoEvents[0];
  }
}

/**
 * Fetch triggered policy frequency analytics.
 */
export async function getPolicyStats() {
  try {
    return await safeFetchJson(`${API_BASE}/audit/policies`);
  } catch (err) {
    return DEMO_POLICIES;
  }
}

/**
 * Intercept an AI agent's proposed action and simulate execution.
 */
export async function interceptAction(payload, includeTrace = true) {
  try {
    const url = `${API_BASE}/intercept${includeTrace ? '?include_trace=true' : ''}`;
    return await safeFetchJson(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  } catch (err) {
    console.info('[AgentGuard] Running client-side policy evaluation sandbox.');
    const result = simulateActionLocally(payload);
    // Prepend to local demo events list
    const newRecord = {
      id: activeDemoEvents.length + 1,
      interception_id: result.interception_id,
      timestamp: result.timestamp,
      user_goal: payload.user_goal,
      action: payload.action,
      target_resource: payload.target_resource,
      destination: payload.destination || 'local',
      decision: result.decision,
      risk_score: result.risk_score,
      risk_level: result.risk_level,
      explanation: result.reason,
      triggered_policies: result.triggered_policies,
      simulation_status: result.simulation_status,
      execution_permitted: result.execution_permitted,
      review_status: result.review_status,
      anomaly_detected: result.anomaly_detected,
      intent_similarity: result.decision === 'ALLOW' ? 0.42 : 0.12,
      simulation_output: result.simulation_output,
    };
    activeDemoEvents = [newRecord, ...activeDemoEvents];
    activeDemoStats = {
      ...activeDemoStats,
      total_events: activeDemoStats.total_events + 1,
      allowed: result.decision === 'ALLOW' ? activeDemoStats.allowed + 1 : activeDemoStats.allowed,
      review: result.decision === 'REVIEW' ? activeDemoStats.review + 1 : activeDemoStats.review,
      blocked: result.decision === 'BLOCK' ? activeDemoStats.blocked + 1 : activeDemoStats.blocked,
    };
    return result;
  }
}

/**
 * Fetch explainable AI decision trace for a specific interception ID.
 */
export async function getDecisionTrace(interceptionId) {
  try {
    return await safeFetchJson(`${API_BASE}/explain/${interceptionId}`);
  } catch (err) {
    const item = activeDemoEvents.find((e) => e.interception_id === interceptionId);
    if (item) {
      return simulateActionLocally({
        user_goal: item.user_goal,
        action: item.action,
        target_resource: item.target_resource,
        destination: item.destination,
      }).decision_trace;
    }
    return simulateActionLocally({
      user_goal: 'General system task',
      action: 'read_project_file',
      target_resource: 'system.log',
    }).decision_trace;
  }
}

/**
 * Fetch proactive security intelligence analytics and threat patterns.
 */
export async function getSecurityIntelligence() {
  try {
    return await safeFetchJson(`${API_BASE}/security/intelligence`);
  } catch (err) {
    return DEMO_INTELLIGENCE;
  }
}
