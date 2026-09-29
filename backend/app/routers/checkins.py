from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..schemas.checkin import CheckinCreate, CheckinResponse
from ..services import checkin_service, progress_service
from ..dependencies.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/goals/{goal_id}/checkins", tags=["checkins"])

@router.post("", response_model=CheckinResponse)
def create_checkin(goal_id: uuid.UUID, checkin_data: CheckinCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    checkin = checkin_service.create_checkin(db, goal_id, checkin_data, current_user)
    # Automatically calculate progress after checkin
    progress_service.calculate_and_save_progress(db, goal_id, checkin.id)
    return checkin

@router.get("", response_model=List[CheckinResponse])
def get_checkins(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return checkin_service.get_checkins(db, goal_id, current_user)

@router.get("/{checkin_id}", response_model=CheckinResponse)
def get_checkin(goal_id: uuid.UUID, checkin_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return checkin_service.get_checkin(db, goal_id, checkin_id, current_user)
