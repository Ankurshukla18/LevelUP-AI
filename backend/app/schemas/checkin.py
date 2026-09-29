from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
import uuid
from ..models.checkin import DifficultyLevel

class CheckinTaskCreate(BaseModel):
    task_id: uuid.UUID
    is_completed: bool
    notes: Optional[str] = None

class CheckinTaskResponse(CheckinTaskCreate):
    id: uuid.UUID
    checkin_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class CheckinBase(BaseModel):
    hours_spent: float = Field(ge=0, le=168)
    accomplishments: str = Field(min_length=1, max_length=5000)
    problems_faced: Optional[str] = Field(default=None, max_length=5000)
    difficulty_level: DifficultyLevel
    self_rating: int = Field(ge=1, le=10)
    notes: Optional[str] = Field(default=None, max_length=5000)

class CheckinCreate(CheckinBase):
    week_id: uuid.UUID
    tasks: List[CheckinTaskCreate]

class CheckinResponse(CheckinBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    week_id: uuid.UUID
    tasks_completed_count: int
    tasks_skipped: Optional[List[str]] = None
    created_at: datetime
    checkin_tasks: List[CheckinTaskResponse] = []

    model_config = ConfigDict(from_attributes=True)
