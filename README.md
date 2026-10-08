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

Based on these dimensions, AgentGuard produces one of three decisions:

* **ALLOW** — Action is verified, safe, and aligned with user intent.
* **REVIEW** — Action contains moderate risk or borderline ambiguity, triggering human-in-the-loop verification.
* **BLOCK** — Action violates security policies, presents severe risk, or is misaligned with the intended task.

---

## Current Phase

**Phase 1 — Project Foundation**

> **Important**: This phase establishes the core directory layout, FastAPI service foundation, test harness, configuration templates, and architectural design. The actual Machine Learning, Risk Assessment, and Policy engines will be implemented in subsequent phases. No active ML detection logic is included in Phase 1.

---

## Technology Stack

* **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic
* **AI/ML (Upcoming Phases):** scikit-learn, sentence-transformers, PyTorch, NumPy, pandas
* **Frontend (Upcoming Phases):** React, Vite, Modern CSS
* **Database:** SQLite (for MVP)
* **Tooling & Environments:** Git/GitHub, Postman, Python Virtual Environments (`venv`)

---

## Project Structure

```text
AgentGuard/
│
├── backend/                  # FastAPI backend service
│   ├── app/                  # Application source code
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint with root & health endpoints
│   │   ├── api/              # API route controllers and endpoints
│   │   ├── models/           # Pydantic schemas and data models
│   │   ├── services/         # Business logic and interceptor services
│   │   └── core/             # Application configuration, settings, and constants
│   └── tests/                # Automated test suite (test_main.py)
│
├── ml/                       # Machine Learning modules (Planned for Phase 3)
│   ├── intent/               # Intent analysis & embedding models
│   ├── context/              # Context tracking & representation
│   ├── anomaly/              # Anomaly detection models
│   └── risk/                 # Multi-factor risk scoring
│
├── policy/                   # Policy rules, RBAC definitions, and guardrails
├── database/                 # SQLite storage and database migrations
├── frontend/                 # React + Vite administrative dashboard (Planned)
├── data/                     # Sample datasets and evaluation benchmarks
├── docs/                     # Documentation and architecture diagrams
│   └── architecture.md       # High-level security architecture specification
│
├── .env.example              # Sample environment configuration
├── .gitignore                # Repository ignore rules (protects large files & models)
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
* Swagger UI Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running the Tests

To verify that the Phase 1 endpoints are functioning correctly:

```powershell
# From the project root:
.\venv\Scripts\python.exe backend\tests\test_main.py
```
Or using pytest:
```powershell
.\venv\Scripts\pytest.exe backend/tests/
```
