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

Based on these dimensions, AgentGuard will eventually produce one of three decisions:

* **ALLOW** — Action is verified, safe, and aligned with user intent.
* **REVIEW** — Action contains moderate risk or borderline ambiguity, triggering human-in-the-loop verification.
* **BLOCK** — Action violates security policies, presents severe risk, or is misaligned with the intended task.

---

## Current Phase

**Phase 3 — Behavioral Anomaly Detection & Risk Assessment**

> **Current Status**: The behavioral intelligence and multi-factor risk assessment engines are active. AgentGuard evaluates historical action trajectories using an unsupervised `IsolationForest` model, classifies target resource sensitivities, aggregates contextual signals, and produces transparent 0–100 normalized risk scores with plain-language explanations via `POST /risk-assessment`.  
> *Note: Deterministic ALLOW/REVIEW/BLOCK policy enforcement rules and human-in-the-loop controls belong to Phase 4. AgentGuard currently performs passive risk analysis and does NOT execute any agent actions.*

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
│   │   ├── api/              # API routers (/analyze, /risk-assessment)
│   │   ├── models/           # Pydantic schemas (RiskAssessmentRequest, Response)
│   │   ├── services/         # Security signals service
│   │   └── core/             # Centralized config, weights & thresholds
│   └── tests/                # Automated test suite (test_main.py, test_analyze.py, test_risk.py)
│
├── ml/                       # Machine Learning intelligence modules
│   ├── intent/               # Intent analysis, embeddings & consistency
│   │   ├── analyzer.py       # Intent analyzer & prototype matcher
│   │   ├── action_normalizer.py # Action dictionary & normalization
│   │   ├── consistency.py    # Intent-action consistency scoring
│   │   └── embeddings.py     # SentenceTransformer embedding service
│   ├── context/              # Context tracking & resource type inference
│   │   └── engine.py         # Structured context engine
│   ├── anomaly/              # Behavioral anomaly detection
│   │   ├── features.py       # 10-dimensional behavioral feature extractor
│   │   └── detector.py       # IsolationForest anomaly detector (synthetic baseline)
│   └── risk/                 # Multi-factor risk scoring
│       ├── resource_classifier.py # Sensitivity heuristics (credentials, system, URLs)
│       └── engine.py         # 0-100 normalized risk engine & explainability
│
├── policy/                   # Policy rules, RBAC definitions (Phase 4)
├── database/                 # SQLite storage and database migrations
├── frontend/                 # React + Vite administrative dashboard (Phase 4)
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
* Swagger UI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running the Tests

To run the complete automated test suite across Phase 1, Phase 2, and Phase 3:

```powershell
.\venv\Scripts\pytest.exe backend/tests/ -v
```
