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

## Current Phase

**Phase 7 — Explainable AI Decision Trace + Security Intelligence**

> **Current Status**: AgentGuard features an end-to-end Explainable AI Decision Trace and proactive Security Intelligence layer. Every security decision is fully explainable as a transparent 7-stage chain of evidence (`INTENT` → `ACTION` → `CONSISTENCY` → `BEHAVIOR` → `RISK` → `POLICY` → `DECISION`). Security analysts can inspect plain-English explanations, audit exact active risk contributions (e.g., `+25` destructive action, `+20` anomaly), evaluate qualitative decision confidence, and detect correlated multi-event threat patterns.  
> *Note: AgentGuard performs active security governance analysis and safe simulation only. It does NOT execute real external commands, file deletions, or network uploads.*

---

## AgentGuard Governance & Audit Pipeline

```text
USER
  ↓
AI AGENT (Proposes Tool Action)
  ↓
AGENTGUARD INTERCEPTOR (Phase 5 Gateway)
  ↓
Intent + Context Analysis (Phase 2)
  ↓
Behavioral Anomaly & Risk Engine (Phase 3)
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
 EXPLANATION ENGINE (Phase 7)
 ├─ Decision Trace & 7-Stage Reasoning Chain
 ├─ Active Risk Factor Contributions (+25, +20...)
 ├─ Plain-English Natural Language Justifications
 └─ Qualitative Decision Confidence (HIGH / MEDIUM / LOW)
       ↓
 AUTOMATIC SANITIZED AUDIT LOGGER (Phase 6)
       ↓
 SQLITE AUDIT DATABASE (`database/agentguard.db`)
       ↓
 SECURITY INTELLIGENCE SERVICE & THREAT DETECTOR (Phase 7)
 ├─ Pattern: Repeated Blocked Actions
 ├─ Pattern: Repeated External Transfers
 ├─ Pattern: Repeated Credential Access Attempts
 ├─ Pattern: Multi-Action Escalation
 └─ Intelligence Summaries & Risk Distributions
       ↓
┌──────────────────────────────────────┬──────────────────────────────┐
│        REST & EXPLAINABILITY APIs    │   REACT + VITE SOC DASHBOARD │
│  /explain/{id}, /security/intel, ... │   Live Visual Decision Trace │
└──────────────────────────────────────┴──────────────────────────────┘
```

### Security Boundary Principle
> **AgentGuard does not execute agent actions.** It evaluates and intercepts proposed actions before execution.
> * **ALLOW** = Policy permits **SAFE SIMULATION** (in-memory mock output).
> * **REVIEW** = Human approval is required before execution (`WAITING_FOR_REVIEW`, `execution_permitted: false`).
> * **BLOCK** = Action is rejected and never simulated (`NOT_EXECUTED`, `execution_permitted: false`).

---

## Technology Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLite
* **AI/ML:** sentence-transformers (`all-MiniLM-L6-v2`), scikit-learn (`IsolationForest`), PyTorch, NumPy, pandas
* **Frontend:** React 18, Vite, Vanilla CSS (SOC Cybersecurity Dark Theme)
* **Database:** SQLite (`database/agentguard.db` auto-created from `database/schema.sql`)
* **Tooling & Environments:** Git/GitHub, Node.js / npm, Python Virtual Environments (`venv`)

---

## Project Structure

```text
AgentGuard/
│
├── backend/                  # FastAPI backend service
│   ├── app/                  # Application source code
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint (/ and /health endpoints)
│   │   ├── api/              # API routers (/analyze, /risk-assessment, /policy-decision, /intercept, /audit)
│   │   │   ├── analyze.py
│   │   │   ├── risk.py
│   │   │   ├── decision.py
│   │   │   ├── intercept.py  # Phase 5 interception endpoint
│   │   │   └── audit.py      # Phase 6 audit logging & dashboard APIs
│   │   ├── database/         # Phase 6 SQLite database access layer
│   │   │   ├── __init__.py
│   │   │   ├── database.py   # Connection management & auto-initialization
│   │   │   ├── models.py     # AuditEventRecord & AuditStatsResponse
│   │   │   └── repository.py # Parameterized DAO queries & metrics aggregation
│   │   ├── models/           # Pydantic schemas across all phases
│   │   │   └── interception.py # Phase 5 InterceptionRequest & Response
│   │   ├── services/         # Orchestration, simulation & audit services
│   │   │   ├── signals.py    # Contextual security signals
│   │   │   ├── interceptor.py# Agent Interceptor orchestrator
│   │   │   ├── simulator.py  # Safe Action Simulator
│   │   │   └── audit.py      # Audit logging & sensitive data sanitization
│   │   └── core/             # Centralized config, weights & thresholds
│   ├── scripts/              # Demonstration scripts
│   │   └── seed_demo_events.py # Seed realistic audit records safely
│   └── tests/                # Automated test suite (56 automated tests)
│       ├── test_main.py      # Phase 1 health and root tests (2 tests)
│       ├── test_analyze.py   # Phase 2 intent and consistency tests (8 tests)
│       ├── test_risk.py      # Phase 3 behavioral anomaly & risk tests (10 tests)
│       ├── test_policy.py    # Phase 4 policy rules & decision tests (11 tests)
│       ├── test_interceptor.py # Phase 5 interception & safety tests (14 tests)
│       └── test_audit.py     # Phase 6 audit persistence & API tests (11 tests)
│
├── frontend/                 # Phase 6 React + Vite SOC Security Dashboard
│   ├── src/
│   │   ├── components/       # Modular dashboard UI components
│   │   │   ├── Header.jsx    # Branding & status indicator
│   │   │   ├── StatCard.jsx  # KPI metrics cards
│   │   │   ├── RiskChart.jsx # Multi-factor risk breakdown
│   │   │   ├── DecisionChart.jsx # Policy verdict distributions
│   │   │   ├── EventTable.jsx# Clickable audit event table
│   │   │   ├── EventDetails.jsx # Detailed audit record modal
│   │   │   ├── SecurityTimeline.jsx # Real-time activity feed
│   │   │   ├── PolicySummary.jsx # Top triggered guardrail analytics
│   │   │   ├── ActionSimulator.jsx # Judge interactive testing sandbox
│   │   │   └── Filters.jsx   # Decision, risk, and anomaly filters
│   │   ├── pages/
│   │   │   └── Dashboard.jsx # Main dashboard view with auto-sync
│   │   ├── services/
│   │   │   └── api.js        # Centralized HTTP API client
│   │   ├── styles/
│   │   │   └── dashboard.css # High-contrast cybersecurity theme
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── policy/                   # Context-Aware Policy Decision Engine (Phase 4)
│   ├── __init__.py           # Policy package exports
│   ├── schemas.py            # DecisionEnum (ALLOW, REVIEW, BLOCK), Request/Response
│   ├── rules.py              # Hierarchical security rules & trigger identifiers
│   └── engine.py             # Policy priority evaluation engine
│
├── ml/                       # Machine Learning intelligence modules
│   ├── intent/               # Intent analysis, embeddings & consistency
│   ├── context/              # Context tracking & resource inference
│   ├── anomaly/              # Behavioral feature extraction & IsolationForest
│   └── risk/                 # Multi-factor risk scoring engine
│
├── database/                 # SQLite storage
│   ├── schema.sql            # Canonical database DDL & indexes
│   └── agentguard.db         # Auto-generated database (git-ignored)
│
├── docs/                     # Documentation and architecture diagrams
│   └── architecture.md       # High-level security architecture specification
│
├── .env.example              # Sample environment configuration
├── .gitignore                # Repository ignore rules (protects models, DB & caches)
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

## Phase 7 — Explainable AI Decision Trace & Security Intelligence

AgentGuard provides full interpretability for every firewall decision. Rather than presenting black-box verdicts or opaque scores, AgentGuard delivers a transparent, verifiable chain of evidence:

### 1. 7-Stage Decision Reasoning Chain
Every interception event traces through a 7-stage analytical pipeline:
1. **INTENT**: Analyzes the user's primary prompt and intent classification.
2. **ACTION**: Evaluates the normalized tool action proposed by the autonomous agent.
3. **CONSISTENCY**: Measures semantic cosine similarity and consistency level (`HIGH`, `MEDIUM`, `LOW`, or `MISMATCH`).
4. **BEHAVIOR**: Detects statistical behavioral sequence anomalies via IsolationForest.
5. **RISK**: Evaluates multi-factor contributions and computes an aggregate score (0–100).
6. **POLICY**: Matches deterministic enterprise guardrails (e.g. `DESTRUCTIVE_ACTION_PREVENTION`, `CRITICAL_RISK_BLOCK`).
7. **DECISION**: Enforces the triad verdict (`ALLOW`, `REVIEW`, or `BLOCK`).

### 2. Concrete Example: Explaining a Blocked Action
```text
USER INTENT
Prepare project report
    ↓
ACTION
Delete project file
    ↓
INTENT-ACTION CONSISTENCY
MISMATCH
    ↓
RISK
HIGH (70.0/100)
    ↓
POLICY
DESTRUCTIVE_ACTION_PREVENTION
    ↓
DECISION
BLOCK
    ↓
REASON
Action does not align with the requested reporting task.
```

### 3. Active Risk Factor Contributions
The dashboard and API expose only the active contributors directly affecting the evaluated score:
* `DESTRUCTIVE_ACTION` (+25) — Action attempts deletion or truncation.
* `EXTERNAL_TRANSFER` (+25) — Outbound data transmission to external destination.
* `SYSTEM_COMMAND` (+25) — Prohibited shell or command execution.
* `SENSITIVE_RESOURCE_ACCESS` (+25) — Credential or protected file target.
* `BEHAVIORAL_ANOMALY` (+20) — Unusual tool invocation trajectory.
* `INTENT_ACTION_MISMATCH` (+15) — Divergence from user objective.

### 4. Qualitative Decision Confidence
AgentGuard displays a qualitative confidence badge (`HIGH`, `MEDIUM`, or `LOW`):
> *"Decision confidence represents the completeness and consistency of AgentGuard's available signals. It is not a calibrated probability of safety."*
* **HIGH**: Clear intent, recognizable action semantics, and deterministic policy rule match.
* **MEDIUM**: Mixed signals or legitimate action on ambiguous resource requiring human review.
* **LOW**: Insufficient context or unrecognized custom operations.

### 5. Multi-Event Threat Pattern Detection
The rule-based `ThreatPatternDetector` correlates audit logs to identify enterprise attack patterns:
* `REPEATED_BLOCKED_ACTIONS` — Multiple blocked attempts in current session.
* `REPEATED_EXTERNAL_TRANSFERS` — Repeated exfiltration attempts to external endpoints.
* `REPEATED_CREDENTIAL_ACCESS` — Suspicious credential file scanning attempts.
* `MULTIPLE_HIGH_RISK_ACTIONS` — Clustering of high/critical risk events.
* `ESCALATION_PATTERN` — Progression from routine file inspection to privileged system execution.

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

### 4. Seed Demonstration Data (Optional)

To populate the dashboard with initial demonstration records:

```powershell
python backend/scripts/seed_demo_events.py
```

### 5. Start FastAPI

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
* Agent Interception: `POST http://127.0.0.1:8000/intercept` (with optional `?include_trace=true`)
* Decision Explainability: `GET http://127.0.0.1:8000/explain/{interception_id}`
* Security Intelligence: `GET http://127.0.0.1:8000/security/intelligence`
* Audit Event Logs: `GET http://127.0.0.1:8000/audit/events`
* Audit Statistics: `GET http://127.0.0.1:8000/audit/stats`
* Policy Analytics: `GET http://127.0.0.1:8000/audit/policies`
* Swagger UI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running the Security Dashboard Frontend

In a separate terminal, launch the React + Vite dashboard:

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173/](http://localhost:5173/) in your browser to view the real-time SOC Security Dashboard.

---

## Running the Automated Tests

To run the complete automated test suite across all Phase 1 through Phase 7 components (70 automated tests):

```powershell
.\venv\Scripts\pytest.exe backend/tests/ -v
```

---

## Phase 8 — Google Cloud & Firebase Deployment

AgentGuard is fully configured for zero-friction cloud deployment using Google tools exclusively:
* **Backend:** Google Cloud Run (containerized FastAPI microservice with CPU-optimized PyTorch).
* **Frontend:** Firebase Hosting (high-speed global CDN for the React/Vite dashboard SPA).
* **Monitoring & Administration:** Google Cloud Console.

### 1. Architecture

```text
┌────────────────────────────┐              ┌────────────────────────────┐
│      Firebase Hosting      │              │      Google Cloud Run      │
│     (React / Vite SPA)     │ ── CORS ───> │     (FastAPI Backend)      │
│  https://*.web.app         │   HTTPS      │  https://*-run.app         │
└────────────────────────────┘              └────────────────────────────┘
```

### 2. Prerequisites & Setup (PowerShell)

Install the Google Cloud SDK and Firebase CLI if not already present:

```powershell
# 1. Install Google Cloud SDK (or via installer from https://cloud.google.com/sdk/docs/install)
winget install Google.CloudSDK

# 2. Install Firebase CLI via npm
npm install -g firebase-tools

# 3. Authenticate with Google
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 4. Authenticate Firebase
firebase login
```

### 3. Deploy Backend to Google Cloud Run

From the project root `Y:\AgentGuard`:

```powershell
# Enable Cloud Run and Artifact Registry APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Deploy backend using source-based build (uses root Dockerfile)
gcloud run deploy agentguard-backend `
  --source . `
  --region us-central1 `
  --platform managed `
  --allow-unauthenticated `
  --memory 1Gi `
  --cpu 1 `
  --set-env-vars "CORS_ORIGINS=https://YOUR_FIREBASE_APP.web.app"
```

Save the generated Cloud Run Service URL (e.g., `https://agentguard-backend-xyz.a.run.app`).

### 4. Build and Deploy Frontend to Firebase Hosting

```powershell
# Set backend URL and build frontend production bundle
$env:VITE_API_BASE_URL="https://agentguard-backend-xyz.a.run.app"
cd frontend
npm run build
cd ..

# Deploy to Firebase Hosting
firebase deploy --only hosting
```

### 5. Verification Commands

```powershell
# Test Cloud Run Health
curl -f https://agentguard-backend-xyz.a.run.app/health

# Test Root Info
curl https://agentguard-backend-xyz.a.run.app/

# Open your live Firebase Hosting URL in browser
Start-Process "https://YOUR_FIREBASE_APP.web.app"
```

