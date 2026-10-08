# AgentGuard

## Overview

AgentGuard is a Context-Aware AI Intent Firewall designed to protect AI agents before they perform external actions. It sits between an autonomous AI agent and the external world (APIs, databases, system shells, file systems) to intercept, evaluate, and govern every proposed operation in real time.

## Problem

As AI agents gain autonomous tool-use capabilities, they can potentially perform actions that are inconsistent with the user's actual goal, triggered by prompt injections, hallucinated reasoning paths, or misaligned tool invocations. Traditional network firewalls only inspect raw network syntax, not semantic intent, leaving agentic workflows vulnerable to unauthorized data exfiltration, destructive command execution, and unintended operations.

## Proposed Solution

AgentGuard intercepts proposed actions and evaluates:

* **User intent** (What the user actually asked for)
* **Context** (System environment, user roles, active workspace)
* **Requested action** (Tool, command, or API call requested)
* **Target resource** (Files, database tables, external URLs)
* **Permissions** (Access privileges and boundaries)
* **Previous behavior** (Session trajectory and anomaly trends)
* **Intent-action consistency** (Semantic alignment between user prompt and tool execution)

Based on these dimensions, AgentGuard produces one of three enforceable decisions:

* **ALLOW** — Action is verified, safe, and aligned with user intent.
* **REVIEW** — Action contains moderate risk or contextual ambiguity, requiring human-in-the-loop verification before execution.
* **BLOCK** — Action violates security policies, presents severe risk, or diverges from the user's intended task.

---

## Current Phase

**Phase 5 — Agent Interception & Safe Action Simulation**

> **Current Status**: The Agent Interception Layer is active at `POST /intercept` (and alias `POST /agent/intercept`). AgentGuard acts as a security checkpoint between an AI agent's tool decisions and potential action execution. Proposed actions are routed through intent-context intelligence, behavioral anomaly detection, multi-factor risk assessment, and hierarchical policy rules. Permitted actions are safely simulated in an in-memory mock environment with strict safety boundaries.  
> *Note: AgentGuard performs active security governance analysis and safe simulation only. It does NOT execute real external commands, file deletions, or network uploads.*

---

## Agent Interception Architecture

```text
USER
  ↓
AI AGENT
  ↓
PROPOSED ACTION
  ↓
AGENTGUARD INTERCEPTOR
  ↓
Intent + Context Analysis (Phase 2)
  ↓
Risk Assessment Engine (Phase 3)
  ↓
Policy Decision Engine (Phase 4)
  ↓
┌──────────────┬────────────────┬──────────────┐
│    ALLOW     │     REVIEW     │    BLOCK     │
└──────┬───────┴───────┬────────┴──────┬───────┘
       ↓               ↓               ↓
  SAFE SIMULATION   HUMAN APPROVAL   REJECT
       ↓               ↓               ↓
 ACTION RESULT     WAITING_FOR_REVIEW BLOCKED
       ↓
 AUDIT EVENT
```

### Security Boundary Principle
> **AgentGuard does not execute agent actions.** It evaluates and intercepts proposed actions before execution.
> * **ALLOW** = Policy permits **SAFE SIMULATION** (mock sandbox output).
> * **REVIEW** = Human approval is required before execution (`WAITING_FOR_REVIEW`, `execution_permitted: false`).
> * **BLOCK** = Action is rejected and never simulated (`NOT_EXECUTED`, `execution_permitted: false`).

---

## Technology Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic
* **AI/ML:** sentence-transformers (`all-MiniLM-L6-v2`), scikit-learn (`IsolationForest`), PyTorch, NumPy, pandas
* **Frontend (Upcoming Phases):** React, Vite, Modern CSS
* **Database (Upcoming Phases):** SQLite (for MVP)
* **Tooling & Environments:** Git/GitHub, Postman, Python Virtual Environments (`venv`)

---

## Project Structure

```text
AgentGuard/
│
├── backend/                  # FastAPI backend service
│   ├── app/                  # Application source code
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint (/ and /health endpoints)
│   │   ├── api/              # API routers (/analyze, /risk-assessment, /policy-decision, /intercept)
│   │   │   ├── analyze.py
│   │   │   ├── risk.py
│   │   │   ├── decision.py
│   │   │   └── intercept.py  # Phase 5 interception endpoint
│   │   ├── models/           # Pydantic schemas across all phases
│   │   │   └── interception.py # Phase 5 InterceptionRequest & Response
│   │   ├── services/         # Orchestration & simulation services
│   │   │   ├── signals.py    # Contextual security signals
│   │   │   ├── interceptor.py# Phase 5 Agent Interceptor orchestrator
│   │   │   └── simulator.py  # Phase 5 Safe Action Simulator
│   │   └── core/             # Centralized config, weights & thresholds
│   └── tests/                # Automated test suite (45 automated tests)
│       ├── test_main.py      # Phase 1 health and root tests (2 tests)
│       ├── test_analyze.py   # Phase 2 intent and consistency tests (8 tests)
│       ├── test_risk.py      # Phase 3 behavioral anomaly & risk tests (10 tests)
│       ├── test_policy.py    # Phase 4 policy rules & decision tests (11 tests)
│       └── test_interceptor.py # Phase 5 interception & safety tests (14 tests)
│
├── policy/                   # Context-Aware Policy Decision Engine (Phase 4)
│   ├── __init__.py           # Policy package exports
│   ├── schemas.py            # DecisionEnum (ALLOW, REVIEW, BLOCK), Request/Response
│   ├── rules.py              # Hierarchical security rules & trigger identifiers
│   └── engine.py             # Policy priority evaluation engine
│
├── ml/                       # Machine Learning intelligence modules
│   ├── intent/               # Intent analysis, embeddings & consistency
│   │   ├── analyzer.py       # Intent analyzer & prototype matcher
│   │   ├── action_normalizer.py # Action dictionary & normalization
│   │   ├── consistency.py    # Intent-action consistency scoring
│   │   └── embeddings.py     # SentenceTransformer embedding service
│   │   └── catalog.py        # Reference catalog
│   ├── context/              # Context tracking & resource type inference
│   │   └── engine.py         # Structured context engine
│   ├── anomaly/              # Behavioral anomaly detection
│   │   ├── features.py       # 10-dimensional behavioral feature extractor
│   │   └── detector.py       # IsolationForest anomaly detector (synthetic baseline)
│   └── risk/                 # Multi-factor risk scoring
│       ├── resource_classifier.py # Sensitivity heuristics (credentials, system, URLs)
│       └── engine.py         # 0-100 normalized risk engine & explainability
│
├── database/                 # SQLite storage and database migrations (Upcoming Phase)
├── frontend/                 # React + Vite administrative dashboard (Upcoming Phase)
├── data/                     # Sample datasets and evaluation benchmarks
├── docs/                     # Documentation and architecture diagrams
│   └── architecture.md       # High-level security architecture specification
│
├── .env.example              # Sample environment configuration
├── .gitignore                # Repository ignore rules (protects models & caches)
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

---

## Interception Demo Scenarios

| Scenario | User Goal | Agent Action | Target Resource | Decision | Simulation Status | Permitted? | Triggered Policies | Reason Summary |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **1. Aligned Reporting** | "Prepare my monthly project report." | `read_project_file` | `project_data.csv` | **ALLOW** | `SIMULATED_SUCCESS` | `true` | `LOW_RISK_ALIGNED_ACTION` | Action consistent with reporting goal; safely simulated mock read. |
| **2. Destructive Mismatch** | "Prepare my monthly project report." | `delete_project_file` | `project_data.csv` | **BLOCK** | `NOT_EXECUTED` | `false` | `DESTRUCTIVE_ACTION`<br>`INTENT_ACTION_MISMATCH` | Action is destructive while user goal is non-destructive reporting. |
| **3. External Exfiltration** | "Prepare my monthly project report." | `upload_external` | `unknown_external_server` | **BLOCK** | `NOT_EXECUTED` | `false` | `SENSITIVE_EXTERNAL_TRANSFER`<br>`INTENT_ACTION_MISMATCH` | Outbound data transmission unrelated to stated goal; completely blocked. |
| **4. Sensitive Credentials** | "Check my project configuration." | `read_project_file` | `credentials.txt` | **REVIEW** | `WAITING_FOR_REVIEW` | `false` | `SENSITIVE_RESOURCE_ACCESS` | Sensitive credentials require human confirmation before access. |
| **5. Shell Escalation** | "Prepare my monthly project report." | `execute_command` | `bash` | **BLOCK** | `NOT_EXECUTED` | `false` | `SYSTEM_COMMAND_RESTRICTION`<br>`CRITICAL_RISK_BLOCK` | Critical risk; shell execution strictly blocked from running. |
| **6. Legitimate Email** | "Send the completed report to my professor." | `send_email` | `professor@university.edu` | **ALLOW** | `SIMULATED_SUCCESS` | `true` | `LOW_RISK_ALIGNED_ACTION` | Email dispatch supports user goal; safely simulated mock dispatch. |

---

## Running the Backend

Follow these steps to set up and run the AgentGuard backend locally:

### 1. Create the Virtual Environment

From the project root (`AgentGuard/`):

```powershell
python -m venv venv
```

### 2. Activate on Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

*(If running on Command Prompt, run `venv\Scripts\activate.bat`. On macOS/Linux, run `source venv/bin/activate`.)*

### 3. Install Requirements

```powershell
python -m pip install -r requirements.txt
```

### 4. Start FastAPI

Navigate into the `backend/` directory and start the Uvicorn server:

```powershell
cd backend
uvicorn app.main:app --reload
```

The interactive documentation will be available at:
* API Root: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
* Intent Analysis: `POST http://127.0.0.1:8000/analyze`
* Risk Assessment: `POST http://127.0.0.1:8000/risk-assessment`
* Policy Decision: `POST http://127.0.0.1:8000/policy-decision` (or alias `POST http://127.0.0.1:8000/decision`)
* Agent Interception: `POST http://127.0.0.1:8000/intercept` (or alias `POST http://127.0.0.1:8000/agent/intercept`)
* Swagger UI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running the Tests

To run the complete automated test suite across all Phase 1 through Phase 5 components (45 automated tests):

```powershell
.\venv\Scripts\pytest.exe backend/tests/ -v
```
