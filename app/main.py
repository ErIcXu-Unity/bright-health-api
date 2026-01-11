from fastapi import FastAPI

from app.routers import health
from app.models import HealthCheck

app = FastAPI(
    title="Bright Health API",
    description="Health data ingestion and retrieval service",
    version="1.0.0"
)

app.include_router(health.router)


@app.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(status="ok")
