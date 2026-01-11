from fastapi import APIRouter, status

from app.database import get_db
from app.models import HealthDataCreate, HealthDataResponse

router = APIRouter(prefix="/users", tags=["health"])


@router.post(
    "/{user_id}/health-data",
    response_model=HealthDataResponse,
    status_code=status.HTTP_201_CREATED
)
def create_health_data(user_id: str, data: HealthDataCreate):
    db = get_db()
    doc_ref = db.collection("users").document(user_id).collection("health_records").document()
    
    record = {
        "timestamp": data.timestamp,
        "steps": data.steps,
        "calories": data.calories,
        "sleepHours": data.sleepHours
    }
    doc_ref.set(record)
    
    return HealthDataResponse(
        id=doc_ref.id,
        userId=user_id,
        timestamp=data.timestamp,
        steps=data.steps,
        calories=data.calories,
        sleepHours=data.sleepHours
    )
