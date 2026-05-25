from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentAnalysisRequest(BaseModel):
    question: str = Field(..., min_length=10, examples=["Why are payments failing?"])
    service: str | None = Field(default=None, examples=["payments-api"])
    severity: Severity = Severity.medium


class EvidenceItem(BaseModel):
    source: str
    title: str
    details: str
    score: float = Field(ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncidentAnalysisResponse(BaseModel):
    incident_id: str
    summary: str
    likely_root_cause: str
    confidence: float = Field(ge=0, le=1)
    impacted_services: list[str]
    evidence: list[EvidenceItem]
    recommended_actions: list[str]


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str

