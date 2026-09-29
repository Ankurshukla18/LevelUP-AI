from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..schemas.progress import ProgressResponse, DashboardAnalyticsResponse
from ..services import analytics_service
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.progress import ProgressRecord
from ..models.goal import Goal

router = APIRouter(tags=["analytics"])

@router.get("/api/goals/{goal_id}/progress", response_model=List[ProgressResponse])
def get_progress(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    records = db.query(ProgressRecord).filter(ProgressRecord.goal_id == goal_id).order_by(ProgressRecord.created_at).all()
    return records

@router.get("/api/dashboard/analytics", response_model=DashboardAnalyticsResponse)
def get_dashboard_analytics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return analytics_service.get_dashboard_analytics(db, current_user)
