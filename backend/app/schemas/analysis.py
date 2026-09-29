from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from ..models.analysis import AdjustmentType, AdjustmentStatus

class AIAnalysisBase(BaseModel):
    summary: str
    went_well: List[str]
    delayed: List[str]
    reasons: List[str]
    recommendations: List[str]
    next_week_focus: List[str]
    roadmap_adjustment_type: AdjustmentType
    adjustment_details: Optional[dict] = None

class AIAnalysisResponse(AIAnalysisBase):
    id: uuid.UUID
    checkin_id: uuid.UUID
    goal_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoadmapAdjustmentBase(BaseModel):
    adjustment_type: str
    details: dict
    status: AdjustmentStatus = AdjustmentStatus.pending

class RoadmapAdjustmentResponse(RoadmapAdjustmentBase):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    analysis_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
