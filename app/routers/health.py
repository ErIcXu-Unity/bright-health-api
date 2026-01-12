from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app import cache
from app.auth import verify_api_key
from app.database import get_db
from app.models import HealthDataCreate, HealthDataResponse, HealthDataListResponse, SummaryResponse

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/users",
    tags=["health"],
    dependencies=[Depends(verify_api_key)]
)

PAGE_SIZE = 50


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {date_str}. Expected DD-MM-YYYY"
        )


@router.post(
    "/{user_id}/health-data",
    response_model=HealthDataResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("60/minute")
def create_health_data(request: Request, user_id: str, data: HealthDataCreate):
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


@router.get(
    "/{user_id}/health-data",
    response_model=HealthDataListResponse
)
@limiter.limit("60/minute")
def get_health_data(
    request: Request,
    user_id: str,
    start: str = Query(..., description="Start date in DD-MM-YYYY format"),
    end: str = Query(..., description="End date in DD-MM-YYYY format"),
    page: int = Query(1, ge=1, description="Page number")
):
    start_date = parse_date(start)
    end_date = parse_date(end)
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    db = get_db()
    collection_ref = db.collection("users").document(user_id).collection("health_records")
    
    query = collection_ref.where("timestamp", ">=", start_date).where("timestamp", "<=", end_date)
    all_docs = list(query.stream())
    
    total_count = len(all_docs)
    start_index = (page - 1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    page_docs = all_docs[start_index:end_index]
    
    data = []
    for doc in page_docs:
        doc_data = doc.to_dict()
        data.append(HealthDataResponse(
            id=doc.id,
            userId=user_id,
            timestamp=doc_data["timestamp"],
            steps=doc_data["steps"],
            calories=doc_data["calories"],
            sleepHours=doc_data["sleepHours"]
        ))
    
    return HealthDataListResponse(
        data=data,
        page=page,
        total_count=total_count,
        has_more=end_index < total_count
    )


@router.get(
    "/{user_id}/summary",
    response_model=SummaryResponse
)
@limiter.limit("60/minute")
def get_summary(
    request: Request,
    user_id: str,
    start: str = Query(..., description="Start date in DD-MM-YYYY format"),
    end: str = Query(..., description="End date in DD-MM-YYYY format")
):
    cache_key = f"summary:{user_id}:{start}:{end}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    start_date = parse_date(start)
    end_date = parse_date(end)
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    db = get_db()
    collection_ref = db.collection("users").document(user_id).collection("health_records")
    
    query = collection_ref.where("timestamp", ">=", start_date).where("timestamp", "<=", end_date)
    all_docs = list(query.stream())
    
    total_steps = 0
    total_calories = 0
    total_sleep = 0.0
    count = len(all_docs)
    
    for doc in all_docs:
        doc_data = doc.to_dict()
        total_steps += doc_data["steps"]
        total_calories += doc_data["calories"]
        total_sleep += doc_data["sleepHours"]
    
    avg_calories = total_calories / count if count > 0 else 0.0
    avg_sleep = total_sleep / count if count > 0 else 0.0
    
    result = SummaryResponse(
        userId=user_id,
        startDate=start,
        endDate=end,
        totalSteps=total_steps,
        averageCalories=round(avg_calories, 2),
        averageSleepHours=round(avg_sleep, 2)
    )
    
    cache.set(cache_key, result, ttl_seconds=300)
    
    return result
