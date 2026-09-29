from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.goal import Goal
from ..models.checkin import WeeklyCheckin
from ..models.progress import ProgressRecord
from ..models.analysis import AIAnalysis, RoadmapAdjustment
from ..ai.mock_ai_service import MockAIService
from ..schemas.analysis import AIAnalysisResponse, RoadmapAdjustmentResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/goals", tags=["ai"])
ai_service = MockAIService()

class AnalyzeRequest(BaseModel):
    checkin_id: uuid.UUID

@router.post("/{goal_id}/analyze", response_model=AIAnalysisResponse)
def analyze_week(goal_id: uuid.UUID, req: AnalyzeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    checkin = db.query(WeeklyCheckin).filter(WeeklyCheckin.id == req.checkin_id, WeeklyCheckin.goal_id == goal_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Checkin not found")
        
    progress = db.query(ProgressRecord).filter(ProgressRecord.goal_id == goal_id).order_by(ProgressRecord.created_at.desc()).first()
    
    analysis_res = ai_service.analyze_week(
        checkin_data={"hours": checkin.hours_spent, "rating": checkin.self_rating},
        goal_info={"name": goal.name},
        progress={"completion_pct": progress.task_completion_pct if progress else 0}
    )
    
    analysis = AIAnalysis(
        checkin_id=checkin.id,
        goal_id=goal_id,
        summary=analysis_res.summary,
        went_well=analysis_res.went_well,
        delayed=analysis_res.delayed,
        reasons=analysis_res.reasons,
        recommendations=analysis_res.recommendations,
        next_week_focus=analysis_res.next_week_focus,
        roadmap_adjustment_type=analysis_res.roadmap_adjustment_type,
        adjustment_details=analysis_res.adjustment_details
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

class AdjustRequest(BaseModel):
    analysis_id: uuid.UUID
    roadmap_id: uuid.UUID

@router.post("/{goal_id}/roadmap/adjust", response_model=RoadmapAdjustmentResponse)
def adjust_roadmap(goal_id: uuid.UUID, req: AdjustRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    analysis = db.query(AIAnalysis).filter(AIAnalysis.id == req.analysis_id).first()
    
    suggestion = ai_service.suggest_adjustment(
        analysis={"type": analysis.roadmap_adjustment_type},
        roadmap={"id": str(req.roadmap_id)},
        remaining_weeks=4
    )
    
    adjustment = RoadmapAdjustment(
        roadmap_id=req.roadmap_id,
        analysis_id=req.analysis_id,
        adjustment_type=suggestion.adjustment_type,
        details=suggestion.details,
        status="applied"
    )
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    return adjustment

@router.post("/{goal_id}/monthly-review")
def monthly_review(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    checkins = db.query(WeeklyCheckin).filter(WeeklyCheckin.goal_id == goal_id).all()
    records = db.query(ProgressRecord).filter(ProgressRecord.goal_id == goal_id).all()
    
    summary = ai_service.generate_monthly_summary(
        goal={"name": goal.name},
        checkins=[{"id": c.id} for c in checkins],
        progress_records=[{"id": r.id} for r in records]
    )
    
    return summary.model_dump()
