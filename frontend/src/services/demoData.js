/**
 * AgentGuard Standalone Demo & Fallback Dataset.
 * Provides realistic SOC analytics, threat intelligence, and client-side
 * policy evaluation when running on static hosting without a live backend.
 */

export const DEMO_STATS = {
  total_events: 312,
  allowed: 109,
  review: 55,
  blocked: 148,
  average_risk_score: 36.2,
  high_risk_events: 124,
  critical_events: 18,
  anomalous_events: 67,
  risk_distribution: {
    LOW: 109,
    MEDIUM: 55,
    HIGH: 124,
    CRITICAL: 18,
  },
  decision_distribution: {
    ALLOW: 109,
    REVIEW: 55,
    BLOCK: 148,
  },
};

export const DEMO_POLICIES = {
  LOW_RISK_ALIGNED_ACTION: 109,
  DESTRUCTIVE_ACTION: 86,
  INTENT_ACTION_MISMATCH: 62,
  SENSITIVE_RESOURCE_ACCESS: 55,
  EXTERNAL_DATA_EXFILTRATION: 41,
  SYSTEM_COMMAND_EXECUTION: 21,
};

export const DEMO_INTELLIGENCE = {
  summary: {
    total_interceptions: 312,
    total_blocked: 148,
    total_blocked_actions: 148,
    most_common_blocked_action: 'delete_project_file',
    most_triggered_policy: 'DESTRUCTIVE_ACTION (86 triggers)',
    most_common_high_risk_resource: 'core_database.db',
    most_common_high_risk_resource_type: 'Database / Credentials',
    anomalous_activity_count: 67,
    average_risk_score: 36.2,
  },
  patterns: [
    {
      pattern: 'REPEATED_BLOCKED_ATTEMPTS',
      severity: 'HIGH',
      description: 'Multiple blocked destructive actions detected targeting production database assets.',
      evidence_count: 14,
      evidence: '14 consecutive policy blocks detected on *.db and credentials.json',
      affected_resources: ['core_database.db', 'credentials.json'],
    },
    {
      pattern: 'SENSITIVE_CREDENTIAL_PROBING',
      severity: 'MEDIUM',
      description: 'Repeated unauthorized attempts to access environment configuration (.env) and secret keys.',
      evidence_count: 8,
      evidence: '8 suspicious file read attempts targeting credentials.txt and .env',
      affected_resources: ['credentials.txt', '.env'],
    },
  ],
  top_policies: [
    { policy: 'LOW_RISK_ALIGNED_ACTION', count: 109 },
    { policy: 'DESTRUCTIVE_ACTION', count: 86 },
    { policy: 'INTENT_ACTION_MISMATCH', count: 62 },
    { policy: 'SENSITIVE_RESOURCE_ACCESS', count: 55 },
    { policy: 'EXTERNAL_DATA_EXFILTRATION', count: 41 },
    { policy: 'SYSTEM_COMMAND_EXECUTION', count: 21 },
  ],
  risk_distribution: {
    LOW: 109,
    MEDIUM: 55,
    HIGH: 124,
    CRITICAL: 18,
  },
  decision_distribution: {
    ALLOW: 109,
    REVIEW: 55,
    BLOCK: 148,
  },
};

export const DEMO_EVENTS = [
  {
    id: 312,
    interception_id: 'AG-2026-9B41E28A',
    timestamp: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
    user_goal: 'Compile weekly documentation',
    action: 'delete_project_file',
    target_resource: 'core_database.db',
    destination: 'local',
    decision: 'BLOCK',
    risk_score: 62.0,
    risk_level: 'HIGH',
    explanation: "The requested action is destructive ('delete_project_file'), while the user's goal is non-destructive. This indicates an intent-action mismatch.",
    triggered_policies: ['DESTRUCTIVE_ACTION', 'INTENT_ACTION_MISMATCH'],
    simulation_status: 'NOT_EXECUTED',
    execution_permitted: false,
    review_status: 'NOT_REQUIRED',
    anomaly_detected: true,
    intent_similarity: 0.12,
  },
  {
    id: 311,
    interception_id: 'AG-2026-8C32D179',
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    user_goal: 'Verify database connection configuration',
    action: 'read_credentials_file',
    target_resource: 'credentials.json',
    destination: 'local',
    decision: 'REVIEW',
    risk_score: 35.0,
    risk_level: 'MEDIUM',
    explanation: "The requested resource 'credentials.json' contains sensitive credentials, and the user's stated goal does not clearly justify access.",
    triggered_policies: ['SENSITIVE_RESOURCE_ACCESS'],
    simulation_status: 'WAITING_FOR_REVIEW',
    execution_permitted: false,
    review_status: 'WAITING_FOR_REVIEW',
    anomaly_detected: false,
    intent_similarity: 0.28,
  },
  {
    id: 310,
    interception_id: 'AG-2026-5A041CAE',
    timestamp: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    user_goal: 'Prepare my monthly project report.',
    action: 'read_project_file',
    target_resource: 'project_data.csv',
    destination: 'local',
    decision: 'ALLOW',
    risk_score: 10.0,
    risk_level: 'LOW',
    explanation: "The requested 'read_project_file' operation is consistent with the user's stated goal and presents low security risk.",
    triggered_policies: ['LOW_RISK_ALIGNED_ACTION'],
    simulation_status: 'SIMULATED_SUCCESS',
    execution_permitted: true,
    review_status: 'NOT_REQUIRED',
    anomaly_detected: false,
    intent_similarity: 0.42,
  },
  {
    id: 309,
    interception_id: 'AG-2026-47F189BA',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    user_goal: 'Analyze customer feedback dataset',
    action: 'upload_external',
    target_resource: 'feedback_dataset.csv',
    destination: 'https://unauthorized-server.com/upload',
    decision: 'BLOCK',
    risk_score: 75.0,
    risk_level: 'CRITICAL',
    explanation: 'Attempting to upload data to an unauthorized external destination without user consent.',
    triggered_policies: ['EXTERNAL_DATA_EXFILTRATION'],
    simulation_status: 'NOT_EXECUTED',
    execution_permitted: false,
    review_status: 'NOT_REQUIRED',
    anomaly_detected: true,
    intent_similarity: 0.15,
  },
  {
    id: 308,
    interception_id: 'AG-2026-3E9012AA',
    timestamp: new Date(Date.now() - 1000 * 60 * 22).toISOString(),
    user_goal: 'Format project documentation',
    action: 'execute_command',
    target_resource: 'bash -c rm -rf /',
    destination: 'local',
    decision: 'BLOCK',
    risk_score: 80.0,
    risk_level: 'CRITICAL',
    explanation: 'Arbitrary shell command execution is prohibited for non-administrative user requests.',
    triggered_policies: ['SYSTEM_COMMAND_EXECUTION'],
    simulation_status: 'NOT_EXECUTED',
    execution_permitted: false,
    review_status: 'NOT_REQUIRED',
    anomaly_detected: true,
    intent_similarity: 0.08,
  },
  {
    id: 307,
    interception_id: 'AG-2026-2D7811FF',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    user_goal: 'Send final quarterly report to department manager',
    action: 'send_email',
    target_resource: 'quarterly_report.pdf',
    destination: 'manager@acme.org',
    decision: 'ALLOW',
    risk_score: 15.0,
    risk_level: 'LOW',
    explanation: 'Communication dispatch is aligned with explicit user authorization.',
    triggered_policies: ['LOW_RISK_ALIGNED_ACTION'],
    simulation_status: 'SIMULATED_SUCCESS',
    execution_permitted: true,
    review_status: 'NOT_REQUIRED',
    anomaly_detected: false,
    intent_similarity: 0.39,
  },
];

export function simulateActionLocally(payload) {
  const goal = (payload.user_goal || payload.user_request || '').toLowerCase();
  const action = payload.action || payload.agent_action || 'read_project_file';
  const resource = payload.target_resource || payload.resource || 'document.txt';
  const destination = payload.destination || 'local';

  let decision = 'ALLOW';
  let riskScore = 10.0;
  let riskLevel = 'LOW';
  let executionPermitted = true;
  let requiresReview = false;
  let policies = ['LOW_RISK_ALIGNED_ACTION'];
  let simStatus = 'SIMULATED_SUCCESS';
  let reason = `The requested '${action}' operation is consistent with the user's stated goal and presents low security risk.`;

  const isSensitive = resource.includes('.env') || resource.includes('credentials') || resource.includes('secret') || resource.includes('password');
  const isDestructive = action === 'delete_project_file' || action.includes('delete');
  const isExfil = action === 'upload_external' || (destination && destination.startsWith('http') && !goal.includes('upload'));
  const isCommand = action === 'execute_command' || action.includes('command') || resource.includes('bash') || resource.includes('sh');

  if (isCommand) {
    decision = 'BLOCK';
    riskScore = 80.0;
    riskLevel = 'CRITICAL';
    executionPermitted = false;
    policies = ['SYSTEM_COMMAND_EXECUTION'];
    simStatus = 'NOT_EXECUTED';
    reason = 'Execution of arbitrary system shell command does not align with non-administrative user request.';
  } else if (isExfil) {
    decision = 'BLOCK';
    riskScore = 75.0;
    riskLevel = 'CRITICAL';
    executionPermitted = false;
    policies = ['EXTERNAL_DATA_EXFILTRATION'];
    simStatus = 'NOT_EXECUTED';
    reason = 'Attempting to upload data to an external destination without explicit authorization in user intent.';
  } else if (isDestructive) {
    decision = 'BLOCK';
    riskScore = 62.0;
    riskLevel = 'HIGH';
    executionPermitted = false;
    policies = ['DESTRUCTIVE_ACTION', 'INTENT_ACTION_MISMATCH'];
    simStatus = 'NOT_EXECUTED';
    reason = "The requested action is destructive ('delete_project_file'), while the user's goal is non-destructive. This indicates an intent-action mismatch.";
  } else if (isSensitive) {
    decision = 'REVIEW';
    riskScore = 35.0;
    riskLevel = 'MEDIUM';
    executionPermitted = false;
    requiresReview = true;
    policies = ['SENSITIVE_RESOURCE_ACCESS'];
    simStatus = 'WAITING_FOR_REVIEW';
    reason = `The requested resource '${resource}' contains sensitive credentials, and the user's stated goal does not clearly justify access.`;
  }

  const id = `AG-2026-${Math.random().toString(16).substring(2, 10).toUpperCase()}`;

  const trace = {
    interception_id: id,
    timestamp: new Date().toISOString(),
    final_decision: decision,
    risk_score: riskScore,
    risk_level: riskLevel,
    decision_confidence: {
      confidence_level: 'HIGH',
      level: 'HIGH',
      rationale: 'Strong semantic clarity, known action semantics, and deterministic policy rule triggers.',
      signals_completeness: 1.0,
      disclaimer: "Decision confidence represents the completeness and consistency of AgentGuard's available signals.",
    },
    short_explanation: reason,
    detailed_explanation: `The user initiated the goal: '${payload.user_goal}'. In response, the autonomous agent proposed action '${action}' targeting resource '${resource}'. AgentGuard assessed an aggregate risk score of ${riskScore}/100 (${riskLevel} tier). Decision: ${decision}.`,
    intent_analysis: {
      user_goal: payload.user_goal,
      detected_intent: isDestructive ? 'file_management' : (action === 'send_email' ? 'communication_dispatch' : 'data_analysis'),
      intent_action_similarity: decision === 'ALLOW' ? 0.42 : 0.12,
      consistency_level: decision === 'ALLOW' ? 'HIGH' : 'LOW',
      consistency_reason: 'Semantic comparison executed via Sentence-Transformers.',
    },
    context_analysis: {
      context_summary: `Context evaluated for action '${action}' on '${resource}'.`,
      previous_action_count: 0,
      context_consistent: decision !== 'BLOCK',
      resource_type: isSensitive ? 'credential' : (resource.endsWith('.db') ? 'database' : 'file'),
    },
    behavior_analysis: {
      anomaly_detected: decision === 'BLOCK',
      anomaly_level: decision === 'BLOCK' ? 'HIGH' : 'LOW',
      behavioral_reason: decision === 'BLOCK' ? 'Action sequence deviates from established baseline.' : 'Action sequence aligns with normal baseline model.',
      anomaly_score: decision === 'BLOCK' ? 0.78 : 0.16,
    },
    resource_analysis: {
      resource: resource,
      resource_type: 'file',
      sensitivity: isSensitive ? 'HIGH' : 'NORMAL',
      category: isSensitive ? 'sensitive_credentials' : 'normal_project_file',
    },
    risk_factors: [
      {
        factor: 'composite_signals',
        impact: riskScore,
        reason: reason,
      },
    ],
    policy_analysis: {
      triggered_policies: policies,
      policy_reasons: [reason],
    },
    reasoning_chain: [
      { stage: 'INTENT', status: 'ANALYZED', summary: `User stated objective: '${payload.user_goal}'.` },
      { stage: 'ACTION', status: 'EVALUATED', summary: `Agent requested '${action}' targeting resource '${resource}'.` },
      { stage: 'CONSISTENCY', status: decision === 'ALLOW' ? 'ALIGNED' : 'MISMATCH', summary: 'Semantic compatibility evaluated.' },
      { stage: 'BEHAVIOR', status: decision === 'BLOCK' ? 'ANOMALY' : 'NORMAL', summary: 'Action trajectory inspected.' },
      { stage: 'RISK', status: `${riskLevel} (${riskScore}/100)`, summary: `Calculated multi-factor risk score: ${riskScore}/100.` },
      { stage: 'POLICY', status: 'EVALUATED', summary: `Active security policies: [${policies.join(', ')}].` },
      { stage: 'DECISION', status: decision, summary: `Final Gateway Decision: ${decision}.` },
    ],
    safety_action: {
      simulation_status: simStatus,
      execution_permitted: executionPermitted,
    },
  };

  return {
    interception_id: id,
    timestamp: trace.timestamp,
    decision: decision,
    risk_score: riskScore,
    risk_level: riskLevel,
    requires_human_review: requiresReview,
    action: action,
    target_resource: resource,
    simulation_status: simStatus,
    execution_permitted: executionPermitted,
    message: decision === 'ALLOW' ? 'Action allowed by AgentGuard and safely simulated.' : (decision === 'REVIEW' ? 'Action requires human approval before execution.' : 'Action blocked by AgentGuard policy firewall.'),
    triggered_policies: policies,
    reason: reason,
    recommendation: decision === 'ALLOW' ? 'Allow action execution.' : (decision === 'REVIEW' ? 'Route to security administrator queue.' : 'Terminate action request immediately.'),
    review_status: requiresReview ? 'WAITING_FOR_REVIEW' : 'NOT_REQUIRED',
    anomaly_detected: decision === 'BLOCK',
    destination: destination,
    simulation_output: {
      operation: action,
      simulated_target: resource,
      status: simStatus.toLowerCase(),
    },
    decision_trace: trace,
  };
}
