# Incident Triage AI - Demo Presentation

## 1. Project Intro

**Incident Triage AI** is an AI-assisted production debugging system for backend teams.

It helps engineers investigate incidents by correlating:

- service logs
- metrics
- deployment history
- runbooks
- simulated business failures

The system produces a structured root cause report with confidence, evidence, impacted services, and recommended remediation steps.

## 2. Problem Statement

Production incidents are hard to debug because information is scattered across many systems.

During an incident, engineers usually need to check:

- logs for errors
- metrics for spikes
- recent deployments
- upstream/downstream services
- runbooks or internal docs
- ownership and escalation paths

This slows down the first response and increases mean time to resolution.

## 3. Solution

Incident Triage AI acts as an internal incident investigation assistant.

An engineer can ask:

```text
Why are payments failing after the latest deployment?
```

The system gathers evidence from backend tools and returns:

- likely root cause
- confidence score
- impacted services
- evidence list
- recommended next actions
- follow-up answers grounded in the generated report

## 4. System Architecture

```text
Incident Console Frontend
        |
        v
Pseudo Commerce APIs
        |
        | trigger realistic failures
        v
Incident Triage AI Backend
        |
        +-- Log Search Tool
        +-- Metrics Tool
        +-- Deployment History Tool
        +-- Runbook Tool
        |
        v
Structured Incident Report
```

## 5. Repositories

### Incident Triage Backend

```text
github.com/dchanda29/incident-triage-ai
```

Purpose:

- core triage API
- agent orchestration
- evidence correlation
- incident report generation

### Frontend Console

```text
github.com/dchanda29/incident-fe
```

Purpose:

- production incident console
- manual incident analysis
- demo scenario buttons
- report visualization

### Pseudo Business APIs

```text
github.com/dchanda29/pseodo-apis
```

Purpose:

- lightweight booking, checkout, payment, inventory, and notification APIs
- realistic failure simulation
- calls Incident Triage AI for automated analysis

## 6. Demo Flow

### Step 1: Open Incident Console

Open the deployed frontend.

Show:

- service selector
- severity selector
- incident question textbox
- live demo scenario buttons

### Step 2: Run Manual Triage

Enter:

```text
Why are payments failing after the latest deployment?
```

Select:

```text
Service: payments-api
Severity: high
```

Click:

```text
Analyze Incident
```

Explain:

The frontend calls the Incident Triage AI backend directly.

### Step 3: Trigger Business Failure

Click:

```text
Payment failure
```

Explain:

The frontend calls the pseudo business API service. That service simulates a failure in the commerce flow and automatically calls the Incident Triage AI backend.

### Step 4: Review AI Report

Walk through:

- summary
- confidence score
- likely root cause
- impacted services
- simulated failure payload
- recommended actions
- evidence items

### Step 5: Explain Backend Design

Highlight:

- the agent is separated from tool implementations
- tools can be replaced with real integrations
- current data is deterministic for demo and testing
- architecture can support CloudWatch, Datadog, Prometheus, GitHub, Slack, or PagerDuty

## 7. Current Capabilities

- FastAPI backend for incident analysis
- structured Pydantic request and response models
- deterministic tool-based agent orchestration
- mock logs, metrics, deployments, and runbooks
- pseudo commerce APIs for realistic demo incidents
- Vite frontend console
- follow-up assistant for contextual incident Q&A
- Docker-ready backend services
- Render-compatible deployment setup
- Vercel frontend deployment

## 8. Example Incident Report

```json
{
  "summary": "payments-api is likely failing because a recent deployment introduced missing or invalid payment provider credentials.",
  "confidence": 0.83,
  "impacted_services": ["payments-api"],
  "recommended_actions": [
    "Verify payment provider secrets in the production environment.",
    "Rollback the latest deployment if credentials cannot be restored quickly.",
    "Add a startup configuration check so missing secrets fail before serving traffic."
  ]
}
```

## 9. Backend Engineering Highlights

This project demonstrates:

- API design
- service-to-service communication
- observability workflow modeling
- agent orchestration
- tool abstraction
- structured data contracts
- deployment-aware backend design
- failure simulation
- production incident thinking

## 10. Why This Is Not Just A Chatbot

The system does not simply answer from a prompt.

It follows an agent-style flow:

```text
question -> gather evidence -> rank signals -> infer root cause -> recommend actions
```

The reasoning is grounded in tool outputs:

- logs
- metrics
- deployments
- runbooks

This makes the system more useful for backend incident response.

## 11. Future Enhancements

- AI follow-up textbox for incident Q&A
- LLM-backed follow-up answers with citations to evidence
- PostgreSQL incident history
- Redis/Celery async triage jobs
- GitHub commit and PR integration
- real log provider integration
- Slack incident bot
- authentication and RBAC
- incident timeline view
- feedback loop for report quality

## 12. Interview Pitch

```text
I built an AI-powered incident triage platform that helps backend teams investigate production failures by correlating logs, metrics, deployment metadata, and runbooks. The system includes a FastAPI triage backend, a pseudo commerce API service for realistic failure simulation, and a frontend incident console for live demos.
```

## 13. Recruiter-Friendly Summary

```text
Built a full-stack AI incident triage system using FastAPI, Vite, Docker, Render, and Vercel. The platform simulates production failures and generates structured root cause reports using logs, metrics, deployment history, and runbooks.
```

## 14. LinkedIn Post Draft

```text
I built Incident Triage AI, a backend-focused AI agent project for production debugging.

The system simulates real incidents across pseudo booking, checkout, payment, and inventory APIs, then calls an AI triage backend to generate a root cause report with evidence, confidence, impacted services, and remediation steps.

Tech stack:
- FastAPI
- Pydantic
- Docker
- Vite
- Render
- Vercel

The goal was to go beyond a simple AI chatbot and build something closer to a real backend operations workflow: logs, metrics, deployments, runbooks, and service-to-service integration.

This was a fun step toward understanding how AI agents can support production engineering and incident response.
```
