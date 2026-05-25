from incident_triage_ai.agent import IncidentTriageAgent
from incident_triage_ai.models import IncidentAnalysisRequest, Severity


def test_agent_detects_payment_credential_incident() -> None:
    agent = IncidentTriageAgent()
    request = IncidentAnalysisRequest(
        question="Why are payments failing after the latest deployment?",
        service="payments-api",
        severity=Severity.high,
    )

    response = agent.analyze(request)

    assert response.confidence > 0.7
    assert "payments-api" in response.impacted_services
    assert "credentials" in response.likely_root_cause.lower()
    assert response.recommended_actions


def test_agent_returns_structured_report_without_service_filter() -> None:
    agent = IncidentTriageAgent()
    request = IncidentAnalysisRequest(
        question="Checkout has many 500 errors and payment failures",
        severity=Severity.critical,
    )

    response = agent.analyze(request)

    assert response.incident_id.startswith("inc_")
    assert response.evidence
    assert "checkout-api" in response.impacted_services
