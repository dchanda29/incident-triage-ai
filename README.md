# Incident Triage AI

Incident Triage AI is a backend-focused AI agent project that helps engineering teams investigate production issues by correlating logs, service metrics, deployment history, and runbook knowledge.

The goal is to demonstrate practical backend engineering depth around APIs, observability, agent tool orchestration, structured outputs, and production-style project organization.

## Problem

Production incidents are noisy. Engineers often need to jump between logs, metrics, deployments, alerts, and runbooks before they can answer basic questions:

- What changed recently?
- Which service is unhealthy?
- Are errors isolated or widespread?
- Is this a deploy regression, dependency issue, or traffic spike?
- What should we do next?

Incident Triage AI provides an agent-style workflow that gathers evidence from multiple backend tools and produces a concise root cause analysis with recommended remediation steps.

## What It Does

Given an incident question such as:

```text
Why are payments failing after the latest deployment?
```

The system:

1. Searches relevant service logs
2. Reads recent deployment metadata
3. Checks service metrics
4. Looks up matching runbook entries
5. Correlates the evidence
6. Returns a structured incident report
7. Answers follow-up questions grounded in the incident report

It also includes a lightweight browser console for demos and local usage.

## Architecture

```text
Incident Console / API Client
        |
        v
FastAPI API Layer
        |
        v
Incident Triage Agent
        |
        +-- Log Search Tool
        +-- Metrics Tool
        +-- Deployment History Tool
        +-- Runbook Tool
        |
        v
Structured Root Cause Report
```

## Tech Stack

- **Python 3.11+**
- **FastAPI** for the backend API
- **Pydantic** for typed request/response models
- **HTML, CSS, and JavaScript** for the incident console UI
- **Uvicorn** for local development
- **Pytest** for automated tests
- **Docker** for containerized execution

The first version uses deterministic mock tools so the project runs locally without external services. The agent layer is intentionally isolated so it can later connect to OpenAI, Datadog, CloudWatch, Prometheus, GitHub, Slack, PagerDuty, or a real incident database.

## Project Structure

```text
incident-triage-ai/
+-- incident_triage_ai/
|   +-- agent.py              # Agent orchestration and evidence correlation
|   +-- config.py             # Runtime settings
|   +-- main.py               # FastAPI app, API routes, and UI route
|   +-- models.py             # API and domain models
|   +-- data/
|   |   +-- deployments.json  # Sample deployment events
|   |   +-- logs.json         # Sample application logs
|   |   +-- metrics.json      # Sample service metrics
|   |   +-- runbooks.json     # Sample remediation knowledge
|   +-- static/
|   |   +-- app.js            # Incident console behavior
|   |   +-- index.html        # Incident console page
|   |   +-- styles.css        # Incident console styles
|   +-- tools/
|       +-- observability.py  # Tool implementations used by the agent
+-- tests/
|   +-- test_agent.py
+-- .env.example
+-- .gitignore
+-- Dockerfile
+-- pyproject.toml
+-- README.md
```

## Getting Started

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Run the API:

```bash
uvicorn incident_triage_ai.main:app --reload
```

Open the health endpoint:

```text
http://127.0.0.1:8000/health
```

Open the incident console:

```text
http://127.0.0.1:8000/
```

## API Usage

Analyze an incident:

```bash
curl -X POST http://127.0.0.1:8000/incidents/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Why are payments failing after the latest deployment?\",\"service\":\"payments-api\",\"severity\":\"high\"}"
```

Ask a follow-up question about an existing report:

```bash
curl -X POST http://127.0.0.1:8000/incidents/follow-up ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"Should we rollback or fix forward?\",\"incident_report\":{...}}"
```

Example response:

```json
{
  "incident_id": "inc_...",
  "summary": "payments-api is likely failing because the latest deployment introduced Stripe credential validation errors.",
  "likely_root_cause": "Recent deployment changed payment configuration and logs show repeated missing STRIPE_SECRET_KEY failures.",
  "confidence": 0.86,
  "impacted_services": ["payments-api", "checkout-api"],
  "evidence": [],
  "recommended_actions": [
    "Verify STRIPE_SECRET_KEY in the production environment.",
    "Rollback payments-api to the previous stable deployment if the secret cannot be restored quickly.",
    "Add a startup configuration check to fail fast before serving traffic."
  ]
}
```

## Running Tests

```bash
pytest
```

## Roadmap

- Add OpenAI tool-calling for natural language reasoning over gathered evidence
- Upgrade follow-up answers from deterministic rules to LLM-backed grounded Q&A
- Persist incidents, evidence, and remediation outcomes in PostgreSQL
- Add Redis/Celery or BullMQ-style async analysis jobs
- Add GitHub integration for recent commits and pull requests
- Add Slack/PagerDuty notification summaries
- Add a React dashboard for incident timelines and service health
- Add authentication and role-based access control

## Portfolio Positioning

This project is designed to support a backend engineering portfolio by showing:

- Clean API design
- Typed data contracts
- Agent orchestration
- Tool abstraction
- Observability workflows
- Incident response thinking
- Testable service boundaries
- Production-ready extension points
