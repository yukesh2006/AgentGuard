# AgentGuard Architecture Specification

> **Phase 4 Status Document**  
> *Status: Active Context-Aware Policy Decision Engine (ALLOW, REVIEW, BLOCK)*  
> *Note: Production proxy interceptors and UI dashboard integration belong to subsequent stages.*

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

## 8. Development Roadmap Across Phases

* **Phase 1 (Completed):** Foundational architecture, repository layout, baseline FastAPI endpoints, hygiene checks, and testing harness.
* **Phase 2 (Completed):** Intent analyzer, action normalizer, context extraction, sentence embeddings (`all-MiniLM-L6-v2`), consistency analyzer, contextual security signals, and `/analyze` endpoint.
* **Phase 3 (Completed):** Behavioral history extraction, IsolationForest anomaly detection, resource classification, multi-factor risk scoring engine, explainability generator, and `/risk-assessment` endpoint.
* **Phase 4 (Completed):** Context-Aware Policy Decision Engine (ALLOW, REVIEW, BLOCK), hierarchical rules, explainability recommendations, and `/policy-decision` endpoint.
* **Phase 5 (Future):** Interactive administrative review dashboard, agent proxy integration, and persistent audit database.
