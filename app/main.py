from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.routers import health
from app.models import HealthCheck

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Bright Health API",
    description="Health data ingestion and retrieval service",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(health.router)


@app.get("/health", response_model=HealthCheck)
def health_check():
    return HealthCheck(status="ok")
