from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from incident_triage_ai.agent import IncidentTriageAgent
from incident_triage_ai.config import settings
from incident_triage_ai.models import HealthResponse, IncidentAnalysisRequest, IncidentAnalysisResponse

app = FastAPI(
    title=settings.app_name,
    description="AI-style incident triage API for backend observability workflows.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="incident_triage_ai/static"), name="static")

agent = IncidentTriageAgent()


@app.get("/", include_in_schema=False)
def console() -> FileResponse:
    return FileResponse("incident_triage_ai/static/index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name, environment=settings.app_env)


@app.post("/incidents/analyze", response_model=IncidentAnalysisResponse)
def analyze_incident(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    return agent.analyze(request)
