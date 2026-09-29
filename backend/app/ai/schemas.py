from pydantic import BaseModel
from typing import List, Optional

class TaskGen(BaseModel):
    title: str
    description: str
    estimated_hours: float
    order: int

class WeekGen(BaseModel):
    week_number: int
    title: str
    description: str
    estimated_hours: float
    tasks: List[TaskGen]

class RoadmapData(BaseModel):
    weeks: List[WeekGen]

class AnalysisResult(BaseModel):
    summary: str
    went_well: List[str]
    delayed: List[str]
    reasons: List[str]
    recommendations: List[str]
    next_week_focus: List[str]
    roadmap_adjustment_type: str
    adjustment_details: Optional[dict] = None

class AdjustmentSuggestion(BaseModel):
    adjustment_type: str
    details: dict

class MonthlySummary(BaseModel):
    month: str
    overall_progress: str
    key_achievements: List[str]
    areas_for_improvement: List[str]
    focus_next_month: str
