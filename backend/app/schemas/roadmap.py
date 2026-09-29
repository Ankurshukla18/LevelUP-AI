from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
import uuid
from ..models.roadmap import WeekStatus

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    order: int

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    is_completed: Optional[bool] = None
    order: Optional[int] = None

class TaskResponse(TaskBase):
    id: uuid.UUID
    week_id: uuid.UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoadmapWeekBase(BaseModel):
    week_number: int
    title: str
    description: Optional[str] = None
    start_date: date
    end_date: date
    estimated_hours: float

class RoadmapWeekUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    status: Optional[WeekStatus] = None

class RoadmapWeekResponse(RoadmapWeekBase):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    status: WeekStatus
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)

class RoadmapBase(BaseModel):
    version: int = 1
    is_active: bool = True
    generated_by_ai: bool = True

class RoadmapResponse(RoadmapBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    weeks: List[RoadmapWeekResponse] = []

    model_config = ConfigDict(from_attributes=True)
