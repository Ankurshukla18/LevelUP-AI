from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from ..models.goal import Goal
from ..schemas.goal import GoalCreate, GoalUpdate
from ..models.user import User

def create_goal(db: Session, goal_data: GoalCreate, user: User) -> Goal:
    db_goal = Goal(**goal_data.model_dump(), user_id=user.id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user: User):
    return db.query(Goal).filter(Goal.user_id == user.id).all()

def get_goal(db: Session, goal_id: uuid.UUID, user: User) -> Goal:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

def update_goal(db: Session, goal_id: uuid.UUID, goal_update: GoalUpdate, user: User) -> Goal:
    goal = get_goal(db, goal_id, user)
    update_data = goal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)
    
    db.commit()
    db.refresh(goal)
    return goal

def delete_goal(db: Session, goal_id: uuid.UUID, user: User):
    goal = get_goal(db, goal_id, user)
    db.delete(goal)
    db.commit()
    return {"message": "Goal deleted successfully"}
