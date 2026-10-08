# AgentGuard Architecture Specification

> **Phase 5 Status Document**  
> *Status: Active Agent Interception Layer & Safe Action Simulation*  
> *Note: Safe simulation only. Real commands, file deletions, and network transfers are strictly prohibited.*

---

## 1. High-Level Overview

**AgentGuard** is a **Context-Aware AI Intent Firewall**. It sits directly between an autonomous AI agent (or LLM application) and external execution environments (such as APIs, databases, file systems, code execution sandboxes, and web scrapers).

Traditional security firewalls inspect raw IP packets or API signatures. AgentGuard inspects **semantic intent, operational context, and behavioral trajectories**: it determines whether what an AI agent is about to do aligns with the user's intent and safety constraints.

---

## 2. High-Level Flow Diagram

```text
       ┌────────────────────────┐
       │   USER / APPLICATION   │
       └───────────┬────────────┘
                   │ User Prompts & Directives
                   ▼
       ┌────────────────────────┐
       │        AI AGENT        │  (LLM reasoning, planning, tool-calling)
       └───────────┬────────────┘
                   │ Proposed Action + Prior Actions History
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                 AGENTGUARD SECURITY GATEWAY                 │
│                                                             │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Intent Engine  │  │ Context Engine │  │Action Parser │  │
│  └────────┬────────┘  └───────┬────────┘  └──────┬───────┘  │
│           │                   │                  │          │
│           └─────────────┬─────┴──────────────────┘          │
│                         ▼                                   │
│        ┌───────────────────────────────────┐                │
│        │   Intent-Action Consistency       │                │
│        │  + Contextual Security Signals    │                │
│        └────────────────┬──────────────────┘                │
│                         ▼                                   │
│        ┌───────────────────────────────────┐                │
│        │   Behavioral Feature Extractor    │                │
│        │  + IsolationForest Anomaly Engine │                │
│        └────────────────┬──────────────────┘                │
│                         ▼                                   │
│        ┌───────────────────────────────────┐                │
│        │   Multi-Factor Risk Engine        │                │
│        │  (0 - 100 Score + Explainability) │                │
│        └────────────────┬──────────────────┘                │
│                         ▼                                   │
│        ┌───────────────────────────────────┐                │
│        │   POLICY DECISION ENGINE (PHASE 4)│                │
│        │    Hierarchical Security Rules    │                │
│        └────────────────┬──────────────────┘                │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
            [ ALLOW / REVIEW / BLOCK ]
                          │
         ┌────────────────┴──────────────┐
         │                               │
    (If ALLOWED)            (If REVIEW or BLOCKED)
         ▼                               ▼
┌──────────────────┐           ┌────────────────────┐
│ ACTION EXECUTION │           │ HALT & ALERT USER  │
└────────┬─────────┘           └─────────┬──────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
        ┌─────────────────────────────────┐
        │     AUDIT LOG + EXPLANATION     │
        └─────────────────────────────────┘
```

---

## 3. Core Component Breakdown

### 3.1. User / Application
The starting point where an authorized user or upstream client supplies instructions, tasks, or system prompts (e.g., *"Summarize our quarterly marketing expenditure"*).

### 3.2. AI Agent
The autonomous LLM or agent runtime (e.g., LangChain, AutoGen, LlamaIndex, custom ReAct agent). The agent reasons over the user prompt and selects tools/actions (e.g., file reads, shell commands, network requests) to accomplish the goal.

### 3.3. AgentGuard Security Gateway
The interception proxy or middleware layer. Before any tool execution or external call is dispatched to the operating system or network, the call is sent to AgentGuard for validation.

### 3.4. Perception & Extraction Layer
* **Intent Engine:** Interprets the user's primary objective, scope, and semantic boundaries using natural language understanding.
* **Context Engine:** Tracks the operational context, including who the user is, environment parameters, session history, previous actions taken, and active system state.
* **Action Parser / Normalizer:** Dissects and maps the agent's proposed call into atomic elements and human-readable descriptions.

### 3.5. Behavioral Anomaly Detection Layer
* **Behavioral Feature Extractor:** Quantifies agent history into a 10-dimensional behavioral feature vector (sequence length, repetition, destructive history, sudden privilege escalation).
* **IsolationForest Detector:** Unsupervised outlier detection trained on baseline agent interaction patterns.

### 3.6. Risk Assessment Engine
Combines consistency, anomaly scores, resource sensitivity, destructive signals, and permission tiers into a transparent 0–100 risk score with human-readable factor explanations.

### 3.7. Context-Aware Policy Decision Engine (Phase 4)
Evaluates full operational context against hierarchical security policies to produce enforceable verdicts: `ALLOW`, `REVIEW`, or `BLOCK`.

---

## 4. Intent → Context → Action Consistency

The core principle behind AgentGuard is **Intent-Context-Action Consistency**:

$$\text{Consistency} = f(\text{User Intent}, \text{Operational Context}, \text{Requested Action})$$

An action cannot be judged purely by its syntax; it must be evaluated in relation to what was requested.

---

## 5. Phase 2 — Intent and Context Intelligence

In Phase 2, AgentGuard introduced the foundational semantic layer:
* **Intent Analysis (`ml/intent/analyzer.py`):** Prototype-based semantic classification with genuine cosine similarity confidence.
* **Action Normalization (`ml/intent/action_normalizer.py`):** Canonical dictionary of representative agent actions with metadata (`is_destructive`, `is_external`, categories).
* **Context Extraction (`ml/context/engine.py`):** Automatic resource type deduction and session context structuring.
* **Semantic Embeddings (`ml/intent/embeddings.py`):** Singleton `all-MiniLM-L6-v2` dense vector encoder.
* **Contextual Security Signals (`backend/app/services/signals.py`):** Rule-based contextual indicators.

---

## 6. Phase 3 — Behavioral Anomaly + Risk Assessment

In Phase 3, AgentGuard added behavioral sequence tracking and multi-factor risk assessment:
* **Behavioral Feature Extractor (`ml/anomaly/features.py`):** Quantifies 10 behavioral metrics from trajectory history.
* **IsolationForest Anomaly Detector (`ml/anomaly/detector.py`):** Detects sudden operational deviations and escalations against a synthetic baseline.
* **Resource Sensitivity Classifier (`ml/risk/resource_classifier.py`):** Categorizes assets into sensitivity tiers.
* **Risk Assessment Engine (`ml/risk/engine.py`):** Computes normalized 0–100 composite risk scores with explainable factor breakdowns.

---

## 7. Phase 4 — Context-Aware Policy Decision Engine

Phase 4 operationalizes AgentGuard into an active enforcement gateway, deployed at `POST /policy-decision` (and alias `POST /decision`).

### 7.1. Why Risk Scoring Alone Is Insufficient
A simple threshold like `if risk_score > 50: BLOCK` fails in real-world AI security:
* **Contextual Justification:** A destructive cleanup (`delete_project_file`) may have a risk score of 45–55, but if the user explicitly asked *"Clean up my project files"*, it should be routed to human **`REVIEW`** rather than blindly blocked.
* **Hard Security Boundaries:** An unauthorized external exfiltration of sensitive credentials might score 60, but must be strictly **`BLOCKED`** immediately regardless of exact thresholds.
* **Intent Alignment:** A benign command execution may score moderate risk, but if it has zero administrative intent, it represents a potential prompt injection attack that must be stopped.

### 7.2. Risk Assessment vs. Policy Decision
> [!IMPORTANT]
> **Risk Assessment $\neq$ Policy Decision**
> * **Risk Assessment (Phase 3)** answers: *"How risky does this action appear given its intent, context, resource, and history?"*
> * **Policy Decision Engine (Phase 4)** answers: *"Given this risk, intent consistency, resource sensitivity, and organization security policies, what operational verdict must be enforced? (`ALLOW`, `REVIEW`, or `BLOCK`)"*

### 7.3. Decision Philosophy

#### 1. ALLOW
Action is granted automatic execution through the gateway:
* User intent and requested action are strongly aligned.
* Risk score is low ($< 25.0$).
* No security policies are violated.
* Target resource is not sensitive credentials.
* No behavioral anomaly or unauthorized destructive action is present.

#### 2. REVIEW
Execution is temporarily suspended and sent to human-in-the-loop (HITL) approval (`requires_human_review: true`):
* Risk score is moderate ($25.0 \le \text{risk} < 75.0$) with contextual ambiguity.
* Sensitive resources (`credentials.txt`, private keys) are accessed without explicit intent clarification.
* Destructive actions (`delete_project_file`) that were requested by the user but require confirmation before irreversible deletion.
* Behavioral deviations that warrant human verification before proceeding.

#### 3. BLOCK
Action execution is immediately terminated (`requires_human_review: false`):
* **Critical Risk:** Compounding threat factors resulting in critical risk score ($\ge 75.0$).
* **Sensitive External Transfer:** Attempting outbound transmission or upload of data without explicit authorization.
* **Dangerous Intent-Action Mismatch:** Performing destructive deletions or exfiltrations during routine, non-destructive tasks.
* **Unauthorized System Command:** Shell command execution (`execute_command`) without administrative user intent.

### 7.4. Policy Hierarchy & Triggered Identifiers
Policies are evaluated according to a strict priority hierarchy:
1. `CRITICAL_RISK_BLOCK`: Blocks critical risk compounding threats.
2. `SENSITIVE_EXTERNAL_TRANSFER`: Blocks unauthorized external data transfers.
3. `INTENT_ACTION_MISMATCH`: Blocks actions with severe intent divergence.
4. `SYSTEM_COMMAND_RESTRICTION`: Blocks arbitrary system shell executions.
5. `SENSITIVE_RESOURCE_ACCESS`: Routes credential/key access to human review.
6. `DESTRUCTIVE_ACTION`: Routes potentially destructive file operations to human review.
7. `HIGH_RISK_REVIEW` / `MEDIUM_RISK_REVIEW`: Routes moderate risk ambiguity to review.
8. `LOW_RISK_ALIGNED_ACTION`: Allows safe, aligned operations.

### 7.5. Structured & Explainable Decision Output
```json
{
  "decision": "BLOCK",
  "risk_score": 50.0,
  "risk_level": "HIGH",
  "requires_human_review": false,
  "triggered_policies": [
    "SENSITIVE_EXTERNAL_TRANSFER",
    "INTENT_ACTION_MISMATCH"
  ],
  "reason": "The requested action attempts to transfer project data to an external destination that is not related to or justified by the user's stated goal.",
  "recommendation": "Block the external transfer and require explicit administrative clearance.",
  "action": "upload_external",
  "target_resource": "https://unknown-server.com/upload"
}
```

---

## 8. Phase 5 — Agent Interception & Safe Action Simulation

Phase 5 operationalizes AgentGuard from a passive advisory analyzer into an **active interception gateway** sitting directly between an AI agent and external execution environments, deployed at `POST /intercept` (and alias `POST /agent/intercept`).

### 8.1. Why an Interception Layer Is Needed
Autonomous AI agents reason, generate execution plans, and invoke tool functions. Without an intermediary interception layer, a compromised or hallucinating agent directly dispatches operations to system shells, databases, file APIs, or remote endpoints.

AgentGuard acts as a **mandatory security checkpoint**:
1. The AI agent proposes an action instead of executing it directly.
2. The AgentGuard Interceptor captures the proposal before any system call occurs.
3. The proposed action is routed through the multi-stage intelligence pipeline:
   - Intent & Context Analysis (Phase 2)
   - Behavioral Anomaly & Multi-Factor Risk Assessment (Phase 3)
   - Hierarchical Policy Decision Engine (Phase 4)
4. Only if policy explicitly permits does the action proceed to safe simulation.

```text
          AI AGENT
              │
              │ "I propose to perform action X on resource Y"
              ▼
       ┌───────────────┐
       │  AGENTGUARD   │
       │  INTERCEPTOR  │
       └───────┬───────┘
               ▼
        Intent + Context Analysis (Phase 2)
               ▼
        Behavioral Anomaly & Risk (Phase 3)
               ▼
         Policy Decision Engine (Phase 4)
               ▼
       ┌───────┼────────┐
       ▼       ▼        ▼
     ALLOW   REVIEW   BLOCK
       │       │        │
       ▼       ▼        ▼
   SIMULATE  WAIT     REJECT
    SAFELY   FOR       ACTION
             REVIEW
```

### 8.2. Zero Duplication Architecture
The interceptor (`backend/app/services/interceptor.py`) does **not** duplicate intelligence or policy logic:
* Intent extraction, sentence embeddings, and consistency analysis are reused from `ml/intent/` and `ml/context/`.
* Behavioral sequence feature extraction and IsolationForest anomaly scoring are reused from `ml/anomaly/`.
* Composite risk scoring and factor attribution are reused from `ml/risk/`.
* Policy hierarchy and rule evaluation are reused from `policy/engine.py`.
The interceptor serves strictly as the orchestration and simulation boundary layer.

### 8.3. Interception Decision Flows

#### 1. ALLOW Flow
* **Condition:** Action aligns with user intent, risk is low, and no security policy triggers.
* **Interceptor Action:** Invokes `SafeActionSimulator.simulate()`.
* **Outcome:** `simulation_status: SIMULATED_SUCCESS`, `execution_permitted: true`.
* **Safety:** Safe mock responses (e.g., simulated file read summary, mock email dispatch confirmation) are generated in-memory. No real file is read or modified.

#### 2. REVIEW Flow
* **Condition:** Action touches sensitive resources (`credentials.txt`), involves user-requested deletions, or exhibits moderate ambiguity.
* **Interceptor Action:** Execution is suspended pending supervisor approval.
* **Outcome:** `simulation_status: WAITING_FOR_REVIEW`, `execution_permitted: false`, `review_status: PENDING`.
* **Safety:** The proposed action is halted immediately. Under no circumstances is the simulated action executed before human sign-off.

#### 3. BLOCK Flow
* **Condition:** Critical risk, system command execution (`bash`, `rm`), unauthorized external data upload (`upload_external`), or intent mismatch.
* **Interceptor Action:** Action is rejected with zero simulation.
* **Outcome:** `simulation_status: NOT_EXECUTED`, `execution_permitted: false`.
* **Safety:** The requested tool is completely denied.

### 8.4. Safe Action Simulator & Hard Safety Boundaries

> [!CAUTION]
> **Core Safety Principle:** AgentGuard NEVER performs real potentially dangerous operations.
> Under no circumstances does AgentGuard execute shell commands, delete local files, access host credential vaults, or make outbound HTTP exfiltration requests.

The `SafeActionSimulator` enforces strict code-level guardrails:
* **Shell Commands (`execute_command`):** Hardcoded guardrail returns `NOT_EXECUTED` (`execution_permitted: false`).
* **Destructive Deletions (`delete_project_file`):** Hardcoded guardrail returns `SIMULATION_ONLY` with dry-run flags; local filesystem is never modified.
* **Network Uploads (`upload_external`):** Hardcoded guardrail returns `NOT_EXECUTED`; zero network packets are transmitted.
* **Credentials Files:** Blocked or placed in `WAITING_FOR_REVIEW`; files are never opened.

### 8.5. Audit-Friendly Interception Event Schema
Each intercepted call produces a uniquely identified, audit-ready structured event:
```json
{
  "interception_id": "AG-2026-4BB184C0",
  "timestamp": "2026-10-09T00:36:13.114022+00:00",
  "decision": "ALLOW",
  "risk_score": 10.0,
  "risk_level": "LOW",
  "requires_human_review": false,
  "action": "read_project_file",
  "target_resource": "project_data.csv",
  "simulation_status": "SIMULATED_SUCCESS",
  "execution_permitted": true,
  "message": "Action allowed by AgentGuard and safely simulated.",
  "triggered_policies": [
    "LOW_RISK_ALIGNED_ACTION"
  ],
  "reason": "The requested 'read_project_file' operation is consistent with the user's stated goal and presents low security risk.",
  "recommendation": "Allow action execution through the security gateway.",
  "review_status": "NOT_REQUIRED",
  "simulation_output": {
    "operation": "read_project_file",
    "simulated_target": "project_data.csv",
    "simulated_records_found": 150,
    "status": "simulated_read_ok"
  }
}
```

---

## 9. Development Roadmap Across Phases

* **Phase 1 (Completed):** Foundational architecture, repository layout, baseline FastAPI endpoints, hygiene checks, and testing harness.
* **Phase 2 (Completed):** Intent analyzer, action normalizer, context extraction, sentence embeddings (`all-MiniLM-L6-v2`), consistency analyzer, contextual security signals, and `/analyze` endpoint.
* **Phase 3 (Completed):** Behavioral history extraction, IsolationForest anomaly detection, resource classification, multi-factor risk scoring engine, explainability generator, and `/risk-assessment` endpoint.
* **Phase 4 (Completed):** Context-Aware Policy Decision Engine (ALLOW, REVIEW, BLOCK), hierarchical rules, explainability recommendations, and `/policy-decision` endpoint.
* **Phase 5 (Completed):** Agent Interception Layer, Safe Action Simulator, mock sandboxed outputs, audit events, and `/intercept` endpoint.
* **Phase 6 (Future):** Interactive administrative review dashboard, persistent database audit logging, and agent framework adapters (LangChain, AutoGen).
