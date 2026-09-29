from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid
from ..database import get_db
from ..schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from ..services import goal_service
from ..dependencies.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/goals", tags=["goals"])

@router.post("", response_model=GoalResponse)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return goal_service.create_goal(db, goal, current_user)

@router.get("", response_model=List[GoalResponse])
def get_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return goal_service.get_goals(db, current_user)

@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return goal_service.get_goal(db, goal_id, current_user)

@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: uuid.UUID, goal_update: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return goal_service.update_goal(db, goal_id, goal_update, current_user)

@router.delete("/{goal_id}")
def delete_goal(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return goal_service.delete_goal(db, goal_id, current_user)
