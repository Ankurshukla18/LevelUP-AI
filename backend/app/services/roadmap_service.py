from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid
from ..models.roadmap import Roadmap, RoadmapWeek, Task
from ..models.goal import Goal
from ..schemas.roadmap import TaskCreate, TaskUpdate, RoadmapWeekUpdate
from ..models.user import User

def get_active_roadmap(db: Session, goal_id: uuid.UUID, user: User) -> Roadmap:
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    roadmap = db.query(Roadmap).filter(Roadmap.goal_id == goal_id, Roadmap.is_active == True).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Active roadmap not found")
    return roadmap

def update_week(db: Session, week_id: uuid.UUID, week_update: RoadmapWeekUpdate, user: User) -> RoadmapWeek:
    week = db.query(RoadmapWeek).join(Roadmap).join(Goal).filter(
        RoadmapWeek.id == week_id, Goal.user_id == user.id
    ).first()
    
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
        
    update_data = week_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(week, key, value)
        
    db.commit()
    db.refresh(week)
    return week

def update_task(db: Session, task_id: uuid.UUID, task_update: TaskUpdate, user: User) -> Task:
    task = db.query(Task).join(RoadmapWeek).join(Roadmap).join(Goal).filter(
        Task.id == task_id, Goal.user_id == user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    return task

def add_task(db: Session, week_id: uuid.UUID, task_data: TaskCreate, user: User) -> Task:
    week = db.query(RoadmapWeek).join(Roadmap).join(Goal).filter(
        RoadmapWeek.id == week_id, Goal.user_id == user.id
    ).first()
    
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
        
    task = Task(**task_data.model_dump(), week_id=week_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: uuid.UUID, user: User):
    task = db.query(Task).join(RoadmapWeek).join(Roadmap).join(Goal).filter(
        Task.id == task_id, Goal.user_id == user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
