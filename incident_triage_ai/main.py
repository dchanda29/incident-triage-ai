from fastapi import FastAPI

from incident_triage_ai.agent import IncidentTriageAgent
from incident_triage_ai.config import settings
from incident_triage_ai.models import HealthResponse, IncidentAnalysisRequest, IncidentAnalysisResponse

app = FastAPI(
    title=settings.app_name,
    description="AI-style incident triage API for backend observability workflows.",
    version="0.1.0",
)

agent = IncidentTriageAgent()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env)


@app.post("/incidents/analyze", response_model=IncidentAnalysisResponse)
def analyze_incident(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    return agent.analyze(request)

