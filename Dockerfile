FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY incident_triage_ai ./incident_triage_ai

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "incident_triage_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]

