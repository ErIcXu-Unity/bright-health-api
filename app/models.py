from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    status: str


class HealthDataCreate(BaseModel):
    timestamp: datetime
    steps: int = Field(ge=0)
    calories: int = Field(ge=0)
    sleepHours: float = Field(ge=0)


class HealthDataResponse(BaseModel):
    id: str
    userId: str
    timestamp: datetime
    steps: int
    calories: int
    sleepHours: float


class HealthDataListResponse(BaseModel):
    data: list[HealthDataResponse]
    page: int
    total_count: int
    has_more: bool


class SummaryResponse(BaseModel):
    userId: str
    startDate: str
    endDate: str
    totalSteps: int
    averageCalories: float
    averageSleepHours: float
