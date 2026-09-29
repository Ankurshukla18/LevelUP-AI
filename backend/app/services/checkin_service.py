from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
from ..models.checkin import WeeklyCheckin, CheckinTask
from ..models.goal import Goal
from ..models.roadmap import Roadmap, RoadmapWeek, Task
from ..schemas.checkin import CheckinCreate
from ..models.user import User

def create_checkin(db: Session, goal_id: uuid.UUID, checkin_data: CheckinCreate, user: User) -> WeeklyCheckin:
    # 1. Verify goal belongs to current authenticated user
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
        
    # 2. Verify week belongs to this specific goal (prevent IDOR across goals/users)
    week = (
        db.query(RoadmapWeek)
        .join(Roadmap, RoadmapWeek.roadmap_id == Roadmap.id)
        .filter(RoadmapWeek.id == checkin_data.week_id, Roadmap.goal_id == goal.id)
        .first()
    )
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found or does not belong to the specified goal."
        )
        
    # 3. Verify all supplied tasks actually belong to this week
    task_models_by_id = {}
    for t in checkin_data.tasks:
        task_model = (
            db.query(Task)
            .filter(Task.id == t.task_id, Task.roadmap_week_id == week.id)
            .first()
        )
        if not task_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {t.task_id} not found in the specified week."
            )
        task_models_by_id[t.task_id] = task_model

    # Calculate completed/skipped tasks
    completed_count = sum(1 for t in checkin_data.tasks if t.is_completed)
    skipped_tasks = [
        task_models_by_id[t.task_id].title
        for t in checkin_data.tasks
        if not t.is_completed and t.task_id in task_models_by_id
    ]
    
    db_checkin = WeeklyCheckin(
        goal_id=goal_id,
        week_id=checkin_data.week_id,
        hours_spent=checkin_data.hours_spent,
        accomplishments=checkin_data.accomplishments,
        problems_faced=checkin_data.problems_faced,
        difficulty_level=checkin_data.difficulty_level,
        self_rating=checkin_data.self_rating,
        notes=checkin_data.notes,
        tasks_completed_count=completed_count,
        tasks_skipped=skipped_tasks if skipped_tasks else None
    )
    
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    
    for task_data in checkin_data.tasks:
        ct = CheckinTask(
            checkin_id=db_checkin.id,
            task_id=task_data.task_id,
            is_completed=task_data.is_completed,
            notes=task_data.notes
        )
        db.add(ct)
        
        # Safely update verified task belonging to current user's goal week
        task_model = task_models_by_id.get(task_data.task_id)
        if task_model:
            task_model.is_completed = task_data.is_completed
            task_model.status = "completed" if task_data.is_completed else "pending"
            task_model.completed_at = datetime.now(timezone.utc) if task_data.is_completed else None
                
    db.commit()
    db.refresh(db_checkin)
    return db_checkin

def get_checkins(db: Session, goal_id: uuid.UUID, user: User):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return db.query(WeeklyCheckin).filter(WeeklyCheckin.goal_id == goal_id).all()

def get_checkin(db: Session, goal_id: uuid.UUID, checkin_id: uuid.UUID, user: User) -> WeeklyCheckin:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    checkin = db.query(WeeklyCheckin).filter(
        WeeklyCheckin.id == checkin_id, WeeklyCheckin.goal_id == goal_id
    ).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Checkin not found")
    return checkin
