from pydantic import BaseModel, ConfigDict
from typing import List, Dict
from datetime import datetime
import uuid

class ProgressBase(BaseModel):
    week_number: int
    task_completion_pct: float
    time_completion_pct: float
    consistency_pct: float
    total_completed_tasks: int
    total_delayed_tasks: int
    total_hours: float
    streak: int

class ProgressResponse(ProgressBase):
    id: uuid.UUID
    goal_id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WeeklyProgressData(BaseModel):
    week: int
    task_pct: float
    time_pct: float

class DashboardAnalyticsResponse(BaseModel):
    active_goals_count: int
    completed_goals_count: int
    overall_completion_pct: float
    total_hours_spent: float
    current_streak: int
    recent_progress: List[ProgressResponse] = []
    weekly_completion_pct: float = 0.0
    goals_by_category: Dict[str, int] = {}
    weekly_progress_data: List[WeeklyProgressData] = []
