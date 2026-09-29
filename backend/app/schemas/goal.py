from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date, datetime
import uuid
from ..models.goal import GoalCategory, GoalPriority, GoalStatus

class GoalBase(BaseModel):
    name: str
    category: GoalCategory
    description: Optional[str] = None
    start_date: date
    target_date: date
    current_level: str
    target_outcome: str
    available_hours_per_week: float = Field(gt=0)
    priority: GoalPriority = GoalPriority.medium
    motivation: Optional[str] = None
    preferred_days: Optional[List[str]] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[GoalCategory] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    target_date: Optional[date] = None
    current_level: Optional[str] = None
    target_outcome: Optional[str] = None
    available_hours_per_week: Optional[float] = None
    priority: Optional[GoalPriority] = None
    motivation: Optional[str] = None
    preferred_days: Optional[List[str]] = None
    status: Optional[GoalStatus] = None

class GoalResponse(GoalBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: GoalStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
