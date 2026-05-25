from uuid import uuid4

from incident_triage_ai.models import EvidenceItem, IncidentAnalysisRequest, IncidentAnalysisResponse
from incident_triage_ai.tools.observability import (
    get_recent_deployments,
    get_service_metrics,
    search_logs,
    search_runbooks,
)


class IncidentTriageAgent:
    """Coordinates observability tools and turns evidence into an incident report."""

    def analyze(self, request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
        evidence = self._gather_evidence(request)
        impacted_services = self._impacted_services(evidence, request.service)
        root_cause = self._infer_root_cause(evidence, request.service)
        confidence = self._confidence(evidence)

        return IncidentAnalysisResponse(
            incident_id=f"inc_{uuid4().hex[:12]}",
            summary=self._summary(root_cause, impacted_services),
            likely_root_cause=root_cause,
            confidence=confidence,
            impacted_services=impacted_services,
            evidence=evidence,
            recommended_actions=self._recommended_actions(evidence),
        )

    def _gather_evidence(self, request: IncidentAnalysisRequest) -> list[EvidenceItem]:
        evidence = [
            *search_logs(request.question, request.service),
            *get_recent_deployments(request.service),
            *get_service_metrics(request.service),
            *search_runbooks(request.question, request.service),
        ]
        return sorted(evidence, key=lambda item: item.score, reverse=True)[:10]

    def _infer_root_cause(self, evidence: list[EvidenceItem], service: str | None) -> str:
        joined = " ".join(item.details.lower() for item in evidence)
        service_label = service or "the affected service"

        if "stripe_secret_key" in joined or "credential" in joined:
            return (
                f"{service_label} is likely failing because a recent deployment introduced "
                "missing or invalid payment provider credentials."
            )

        if "timeout" in joined or "latency" in joined:
            return (
                f"{service_label} is likely degraded by upstream latency or timeout failures."
            )

        if "database" in joined or "connection pool" in joined:
            return (
                f"{service_label} is likely impacted by database connectivity or pool exhaustion."
            )

        return (
            f"{service_label} has correlated log, metric, and deployment signals, but the exact "
            "root cause needs deeper investigation."
        )

    def _recommended_actions(self, evidence: list[EvidenceItem]) -> list[str]:
        joined = " ".join(item.details.lower() for item in evidence)

        if "stripe_secret_key" in joined or "credential" in joined:
            return [
                "Verify payment provider secrets in the production environment.",
                "Rollback the latest deployment if credentials cannot be restored quickly.",
                "Add a startup configuration check so missing secrets fail before serving traffic.",
            ]

        if "timeout" in joined or "latency" in joined:
            return [
                "Check upstream dependency health and recent latency changes.",
                "Increase timeout budgets only after confirming the dependency is healthy.",
                "Enable circuit breaking or graceful degradation for the affected path.",
            ]

        if "database" in joined or "connection pool" in joined:
            return [
                "Inspect database connection pool usage and slow queries.",
                "Scale the database or reduce worker concurrency if the pool is saturated.",
                "Add query-level metrics for the affected endpoint.",
            ]

        return [
            "Review the highest scoring evidence items first.",
            "Compare the latest deployment with the last known healthy version.",
            "Escalate to the owning service team with the incident report.",
        ]

    def _summary(self, root_cause: str, impacted_services: list[str]) -> str:
        services = ", ".join(impacted_services) if impacted_services else "unknown services"
        return f"{root_cause} Impacted services: {services}."

    def _confidence(self, evidence: list[EvidenceItem]) -> float:
        if not evidence:
            return 0.0

        source_count = len({item.source for item in evidence})
        average_score = sum(item.score for item in evidence[:5]) / min(len(evidence), 5)
        return round(min(0.95, average_score * 0.7 + source_count * 0.08), 2)

    def _impacted_services(self, evidence: list[EvidenceItem], requested_service: str | None) -> list[str]:
        services = {
            item.metadata["service"]
            for item in evidence
            if isinstance(item.metadata, dict) and "service" in item.metadata
        }

        if requested_service:
            services.add(requested_service)

        return sorted(services)

