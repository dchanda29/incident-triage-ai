from uuid import uuid4

from incident_triage_ai.models import (
    EvidenceItem,
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
    IncidentFollowUpRequest,
    IncidentFollowUpResponse,
)
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

    def answer_follow_up(self, request: IncidentFollowUpRequest) -> IncidentFollowUpResponse:
        report = request.incident_report
        question = request.question.lower()
        evidence_titles = [item.title for item in report.evidence[:3]]

        if any(word in question for word in {"rollback", "revert", "deploy"}):
            answer = self._rollback_answer(report)
        elif any(word in question for word in {"first", "start", "priority", "check"}):
            answer = self._first_check_answer(report)
        elif any(word in question for word in {"prevent", "avoid", "future", "again"}):
            answer = self._prevention_answer(report)
        elif any(word in question for word in {"confirm", "verify", "prove"}):
            answer = self._verification_answer(report)
        else:
            answer = (
                f"Based on the current report, focus on the likely root cause first: "
                f"{report.likely_root_cause} The strongest next step is: "
                f"{report.recommended_actions[0] if report.recommended_actions else 'review the top evidence items.'}"
            )

        return IncidentFollowUpResponse(
            answer=answer,
            grounded_in=evidence_titles,
            suggested_next_questions=[
                "What should I check first?",
                "How do I verify the root cause?",
                "Should I rollback or fix forward?",
            ],
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

    def _rollback_answer(self, report: IncidentAnalysisResponse) -> str:
        joined = self._report_text(report)
        if "deployment" in joined and ("credential" in joined or "secret" in joined):
            return (
                "Rollback is reasonable if restoring the missing credential will take longer than "
                "your incident SLA. If the secret can be restored quickly, fix forward by updating "
                "the production environment, then verify error rate recovery for the impacted service."
            )

        if "deployment" in joined:
            return (
                "Compare the latest deployment with the last healthy version. Roll back if the failure "
                "started immediately after deploy and the owner cannot produce a low-risk fix quickly."
            )

        return (
            "Do not rollback only because the service is unhealthy. First confirm the issue maps to a "
            "recent deploy; otherwise prioritize dependency, database, or configuration checks."
        )

    def _first_check_answer(self, report: IncidentAnalysisResponse) -> str:
        if report.recommended_actions:
            return (
                f"Start with this action: {report.recommended_actions[0]} Then check the top evidence "
                f"item, because it has the strongest signal in the report."
            )

        return "Start by reviewing the highest-scored evidence item and the latest deployment."

    def _prevention_answer(self, report: IncidentAnalysisResponse) -> str:
        joined = self._report_text(report)
        if "credential" in joined or "secret" in joined:
            return (
                "Add startup configuration validation, deployment smoke tests for payment authorization, "
                "and alerting on provider credential errors. This prevents the service from accepting "
                "traffic with missing production secrets."
            )

        if "timeout" in joined or "latency" in joined:
            return (
                "Add dependency latency alerts, circuit breakers, and timeout dashboards. Also track "
                "retry volume so degradation does not amplify traffic during incidents."
            )

        return (
            "Turn the top evidence into a monitor, add a runbook entry for the remediation path, and "
            "store this incident outcome so future triage can compare against it."
        )

    def _verification_answer(self, report: IncidentAnalysisResponse) -> str:
        joined = self._report_text(report)
        if "credential" in joined or "secret" in joined:
            return (
                "Verify by checking the production secret value exists, restarting or refreshing the "
                "affected service if needed, and confirming payment 500s drop while successful "
                "authorizations increase."
            )

        if "timeout" in joined or "latency" in joined:
            return (
                "Verify by comparing p95 latency, timeout count, and upstream health before and after "
                "the suspected failure window."
            )

        return (
            "Verify by checking whether the highest-scored evidence item changes after the remediation. "
            "The report should show lower error signals and fewer related log entries."
        )

    def _report_text(self, report: IncidentAnalysisResponse) -> str:
        evidence = " ".join(item.details for item in report.evidence)
        actions = " ".join(report.recommended_actions)
        return f"{report.summary} {report.likely_root_cause} {evidence} {actions}".lower()
