# AgentGuard Architecture Specification

> **Phase 3 Status Document**  
> *Status: Active Behavioral Anomaly Detection & Multi-Factor Risk Assessment Engine*  
> *Note: Deterministic ALLOW/REVIEW/BLOCK policy enforcement rules remain scheduled for Phase 4.*

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
│        │      Policy Engine (Phase 4)      │                │
│        └────────────────┬──────────────────┘                │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
            [ ALLOW / REVIEW / BLOCK ] (Phase 4)
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

### 3.7. The Triad Decision Model (Phase 4)
Every proposed action eventually maps to one of three decisions:
* **ALLOW:** The action is consistent with user intent and complies with security policies.
* **REVIEW:** The action has moderate risk, unexpected side effects, or borderline intent alignment. Human-in-the-loop (HITL) approval is requested.
* **BLOCK:** The action represents a clear threat, policy violation, prompt injection exploitation, or unauthorized exfiltration.

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

Phase 3 introduces behavioral sequence monitoring and a multi-factor risk assessment engine accessible via `POST /risk-assessment`.

### 6.1. Behavioral History & Feature Extraction (`ml/anomaly/features.py`)
AI agents rarely execute malicious actions in isolation; threats often emerge as sudden deviations or privilege escalations after benign tasks. The feature extractor converts session trajectories into 10 measurable metrics:
1. `history_length`: Total volume of prior actions in the active session.
2. `unique_action_count`: Number of distinct action types executed.
3. `destructive_history_count`: Cumulative destructive actions in session history.
4. `current_is_destructive`: Flag indicating if the proposed action is destructive.
5. `external_history_count`: Cumulative external uploads/transfers in session history.
6. `current_is_external`: Flag indicating if the proposed action contacts external endpoints.
7. `system_command_history_count`: Prior system shell commands executed.
8. `current_is_system_command`: Flag indicating if the proposed action invokes `execute_command`.
9. `action_repetition_count`: Frequency of current action within recent history.
10. `escalation_anomaly_flag`: Indicates sudden high-risk tool invocation following a purely benign, non-destructive history.

### 6.2. IsolationForest Anomaly Detection (`ml/anomaly/detector.py`)
* **Algorithm:** Unsupervised `IsolationForest` (`n_estimators=100`, `contamination=0.10`, `random_state=42`) from `scikit-learn`.
* **Methodology Disclosure:**
  > [!NOTE]
  > **Synthetic Baseline Transparency:** The IsolationForest detector is trained on a synthetic baseline representing routine agent workflows (iterative data reads, analyses, queries, formatting, and benign repetition). In a production cybersecurity deployment, this baseline would be trained on empirical historical audit logs and agent telemetry. No claims of "99% production cyber accuracy" are made.
* **Scoring:** Calculates continuous decision scores:
  * Inliers ($\ge 0.0$): Regular trajectory, `severity = "low"`.
  * Outliers ($< 0.0$): Deviant trajectory; if score $< -0.08$, `severity = "high"`, otherwise `"medium"`.

### 6.3. Resource Sensitivity Classification (`ml/risk/resource_classifier.py`)
Heuristic classifier determining asset sensitivity:
* `sensitive_credentials`: File names or paths containing `password`, `secret`, `credential`, `key`, `token`, `.env`, etc.
* `system_resource`: Shell interpreters, administrative paths (`bash`, `cmd`, `powershell`, `/dev/`).
* `external_destination`: Remote endpoints (`http://`, `https://`).
* `normal_project_file`: Local data files (`.csv`, `.tsv`, `.json`, `.parquet`).
* `normal_document`: Standard document formats (`.pdf`, `.docx`, `.md`).

### 6.4. Transparent Risk Scoring Formula (`ml/risk/engine.py`)
AgentGuard calculates a normalized composite risk score from $0.0$ to $100.0$:

$$\text{RiskScore} = \min\left(100.0, \, \sum \text{FactorImpacts}\right)$$

#### Configurable Risk Factor Weights:
| Risk Factor | Config Weight | Condition for Impact |
| :--- | :---: | :--- |
| **Intent Inconsistency** | 25.0 | Low semantic compatibility ($< 0.15$) adds $25.0$; medium compatibility adds $10.0$; high adds $0.0$. |
| **Destructive Action** | 25.0 | Action is destructive while user intent is purely observational or generative. |
| **External Data Transfer** | 25.0 | Outbound transfer to external destination without explicit authorization in user request. |
| **System Execution** | 25.0 | Shell command execution requested outside administrative intent. |
| **Resource Sensitivity** | 25.0 | Target asset is categorized as `sensitive_credentials` or privileged `system_resource`. |
| **Behavioral Anomaly** | 20.0 | High IsolationForest anomaly severity adds $20.0$; medium severity adds $12.0$. |
| **Permission Mismatch** | 15.0 | Standard user account invokes administrative or privileged actions without delegation. |

### 6.5. Risk Level Categorization
The numerical score maps into transparent risk bands:
* **`LOW` (0.0 – 24.9):** Consistent, non-destructive, normal behavioral trajectory.
* **`MEDIUM` (25.0 – 49.9):** Moderate ambiguity, access to sensitive assets, or slight behavioral deviation.
* **`HIGH` (50.0 – 74.9):** Significant inconsistency, unauthorized external transfer, or unrequested destructive action.
* **`CRITICAL` (75.0 – 100.0):** Multiple compounding threat signals (e.g., sudden shell escalation + low intent alignment + permission mismatch).

### 6.6. Risk Explanation & Transparency
Every risk assessment returns structured contributing factors:
```json
{
  "factor": "destructive_action",
  "impact": 25.0,
  "reason": "Action 'delete_project_file' is destructive, but user goal does not request file or resource deletion."
}
```
Avoiding black-box outputs ensures human auditors and downstream agents understand exactly *why* risk was assigned.

### 6.7. Risk Assessment vs. Policy Decision
> [!IMPORTANT]
> **Risk Assessment $\neq$ Policy Decision**
> * **Risk Assessment (Phase 3)** answers: *"How risky does this action appear given its intent, context, resource, and history?"*
> * **Policy Engine (Phase 4)** will answer: *"Given this risk score, organizational rules, and user configuration, what action should AgentGuard take? (`ALLOW`, `REVIEW`, or `BLOCK`)"*

---

## 7. Development Roadmap Across Phases

* **Phase 1 (Completed):** Foundational architecture, repository layout, baseline FastAPI endpoints, hygiene checks, and testing harness.
* **Phase 2 (Completed):** Intent analyzer, action normalizer, context extraction, sentence embeddings (`all-MiniLM-L6-v2`), consistency analyzer, contextual security signals, and `/analyze` endpoint.
* **Phase 3 (Completed):** Behavioral history extraction, IsolationForest anomaly detection, resource classification, multi-factor risk scoring engine, explainability generator, and `/risk-assessment` endpoint.
* **Phase 4 (Upcoming):** Deterministic Policy Engine (ALLOW / REVIEW / BLOCK), configurable thresholds, administrative override options, audit logging, and human-in-the-loop review interfaces.
