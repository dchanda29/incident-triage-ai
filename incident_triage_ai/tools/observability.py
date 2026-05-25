import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from incident_triage_ai.models import EvidenceItem

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@lru_cache
def _load_json(file_name: str) -> list[dict[str, Any]]:
    with (DATA_DIR / file_name).open(encoding="utf-8") as file:
        return json.load(file)


def search_logs(question: str, service: str | None = None) -> list[EvidenceItem]:
    keywords = _keywords(question)
    matches: list[EvidenceItem] = []

    for row in _load_json("logs.json"):
        if service and row["service"] != service:
            continue

        message = row["message"].lower()
        keyword_hits = sum(1 for keyword in keywords if keyword in message)
        severity_boost = 0.25 if row["level"] in {"ERROR", "CRITICAL"} else 0
        score = min(1.0, 0.35 + (keyword_hits * 0.15) + severity_boost)

        if keyword_hits or row["level"] in {"ERROR", "CRITICAL"}:
            matches.append(
                EvidenceItem(
                    source="logs",
                    title=f"{row['level']} in {row['service']}",
                    details=row["message"],
                    score=score,
                    metadata=row,
                )
            )

    return sorted(matches, key=lambda item: item.score, reverse=True)[:5]


def get_recent_deployments(service: str | None = None) -> list[EvidenceItem]:
    deployments = _load_json("deployments.json")
    if service:
        deployments = [deployment for deployment in deployments if deployment["service"] == service]

    return [
        EvidenceItem(
            source="deployments",
            title=f"Deployment {deployment['version']} to {deployment['service']}",
            details=deployment["summary"],
            score=0.75 if deployment["status"] == "deployed" else 0.4,
            metadata=deployment,
        )
        for deployment in deployments[:5]
    ]


def get_service_metrics(service: str | None = None) -> list[EvidenceItem]:
    metrics = _load_json("metrics.json")
    if service:
        metrics = [metric for metric in metrics if metric["service"] == service]

    evidence = []
    for metric in metrics:
        error_rate = float(metric["error_rate_percent"])
        latency = int(metric["p95_latency_ms"])
        score = min(1.0, (error_rate / 10) + (latency / 3000))

        evidence.append(
            EvidenceItem(
                source="metrics",
                title=f"Metrics anomaly for {metric['service']}",
                details=(
                    f"error_rate={error_rate}%, p95_latency={latency}ms, "
                    f"traffic={metric['requests_per_minute']} rpm"
                ),
                score=score,
                metadata=metric,
            )
        )

    return sorted(evidence, key=lambda item: item.score, reverse=True)[:5]


def search_runbooks(question: str, service: str | None = None) -> list[EvidenceItem]:
    keywords = _keywords(question)
    matches: list[EvidenceItem] = []

    for runbook in _load_json("runbooks.json"):
        if service and service not in runbook["services"]:
            continue

        searchable = f"{runbook['title']} {runbook['symptoms']} {' '.join(runbook['actions'])}".lower()
        keyword_hits = sum(1 for keyword in keywords if keyword in searchable)
        if keyword_hits:
            matches.append(
                EvidenceItem(
                    source="runbooks",
                    title=runbook["title"],
                    details=runbook["symptoms"],
                    score=min(1.0, 0.45 + keyword_hits * 0.12),
                    metadata=runbook,
                )
            )

    return sorted(matches, key=lambda item: item.score, reverse=True)[:3]


def _keywords(text: str) -> set[str]:
    ignored = {"the", "is", "are", "why", "what", "after", "latest", "and", "for", "with"}
    return {word.strip(".,?!").lower() for word in text.split() if len(word) > 2} - ignored

