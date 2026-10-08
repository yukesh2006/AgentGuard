# AgentGuard Architecture Specification

> **Phase 2 Status Document**  
> *Status: Active Intelligence Foundation (Intent, Context & Semantic Consistency)*  
> *Note: Final Risk scoring and deterministic ALLOW/REVIEW/BLOCK Policy engines remain scheduled for Phase 3 and 4.*

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
│           │   Risk Assessment Engine   │  (Phase 3)         │
│           └─────────────┬──────────────┘                    │
│                         ▼                                   │
│           ┌────────────────────────────┐                    │
│           │       Policy Engine        │  (Phase 3/4)       │
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

## 5. Phase 2 — Intent and Context Intelligence

In Phase 2, AgentGuard introduces the first functional AI/ML intelligence layer, deployed under `POST /analyze`.

### 5.1. Intent Analysis (`ml/intent/analyzer.py`)
The Intent Analyzer parses natural-language prompts into structured operational intents without fabricating synthetic metrics:
* **Semantic Category Mapping:** Computes dense vector embeddings of user requests and measures cosine distance against canonical intent prototypes (`report_generation`, `data_analysis`, `file_management`, `communication_dispatch`, `system_administration`, `information_retrieval`).
* **Goal Extraction:** Cleans and normalizes the core user directive.
* **Genuine ML Confidence:** Assigns a real cosine similarity score derived directly from the embedding model as the confidence metric.

### 5.2. Action Normalization (`ml/intent/action_normalizer.py`)
AI agents invoke tools via programmatic names (e.g., `read_project_file`, `upload_external`, `delete_project_file`). The Action Normalizer:
* Translates raw tool names into human-understandable descriptions (e.g., `"Read a project data file"`, `"Upload data to an external destination"`).
* Enriches each action with functional security metadata (e.g., `is_destructive`, `is_external`, functional category).
* Rejects unknown or malformed action verbs with clear client errors.

### 5.3. Context Extraction (`ml/context/engine.py`)
The Context Engine builds a unified context frame:
* Inters resource categories automatically from target strings (`file`, `network_endpoint`, `email_recipient`, `database`, `general_resource`).
* Associates active session parameters, user privilege tiers, and prior execution history.

### 5.4. Semantic Embeddings (`ml/intent/embeddings.py`)
* Employs the `all-MiniLM-L6-v2` model from `sentence-transformers`.
* Generates 384-dimensional dense semantic vectors.
* Encapsulated in a singleton pattern to eliminate model reloading latency.
* Preserves zero-footprint repository safety by utilizing host user cache directories (`~/.cache/huggingface/hub`) outside the Git tree.

### 5.5. Intent-Action Consistency (`ml/intent/consistency.py`)
Evaluates the semantic distance between what the user requested and what the agent is attempting:
$$\text{ActionContext} = \text{Action Description} + \text{" on "} + \text{Target Resource}$$
$$\text{Similarity} = \cos(\mathbf{v}_{\text{intent}}, \mathbf{v}_{\text{action\_context}})$$
* **Configurable Compatibility Categorization:**
  * **High:** $\text{Similarity} \ge 0.33$
  * **Medium:** $0.15 \le \text{Similarity} < 0.33$
  * **Low:** $\text{Similarity} < 0.15$

### 5.6. Contextual Security Signals (`backend/app/services/signals.py`)
Generates actionable security signals reflecting potential risk factors:
* `intent_action_consistency`: Assesses degree of semantic alignment.
* `destructive_action_anomaly`: Flags irreversible file deletions requested during non-destructive tasks.
* `external_data_transfer`: Flags outbound uploads not authorized by the user prompt.
* `unrelated_system_execution`: Flags shell execution during routine data or report operations.
* `authorized_resource_access`: Acknowledges normal, non-destructive reads of expected files.
* `communication_dispatch_aligned`: Confirms valid dispatch when communication was explicitly requested.

> [!IMPORTANT]
> **Semantic similarity is NOT the final security decision.**  
> Semantic compatibility is an essential intelligence signal, but high similarity alone does not prove an action is safe (e.g., an agent can semantically describe a malicious deletion). In Phase 3, these similarity metrics and contextual signals will serve as raw features feeding into the multi-factor Risk Assessment and deterministic Policy engines.

---

## 6. Development Roadmap Across Phases

* **Phase 1 (Completed):** Foundational architecture, repository layout, baseline FastAPI endpoints, hygiene checks, and testing harness.
* **Phase 2 (Completed):** Intent analyzer, action normalizer, context extraction, sentence embeddings (`all-MiniLM-L6-v2`), consistency analyzer, contextual security signals, and `/analyze` endpoint.
* **Phase 3 (Upcoming):** Risk scoring engine, behavioral anomaly scoring, and deterministic policy rule engine (ALLOW / REVIEW / BLOCK).
* **Phase 4:** Human-in-the-loop review dashboard (React/Vite) and agent proxy integration.
