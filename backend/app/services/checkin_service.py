from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from ..models.checkin import WeeklyCheckin, CheckinTask
from ..models.goal import Goal
from ..models.roadmap import RoadmapWeek, Task
from ..schemas.checkin import CheckinCreate
from ..models.user import User

def create_checkin(db: Session, goal_id: uuid.UUID, checkin_data: CheckinCreate, user: User) -> WeeklyCheckin:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
        
    week = db.query(RoadmapWeek).filter(RoadmapWeek.id == checkin_data.week_id).first()
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
        
    # Calculate completed/skipped tasks
    completed_count = sum(1 for t in checkin_data.tasks if t.is_completed)
    skipped_tasks = []
    
    for t in checkin_data.tasks:
        if not t.is_completed:
            task_model = db.query(Task).filter(Task.id == t.task_id).first()
            if task_model:
                skipped_tasks.append(task_model.title)
    
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
        
        # update actual task status
        if task_data.is_completed:
            actual_task = db.query(Task).filter(Task.id == task_data.task_id).first()
            if actual_task:
                actual_task.is_completed = True
                
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
