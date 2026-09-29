from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import timedelta
from ..database import get_db
from ..schemas.roadmap import RoadmapResponse, RoadmapWeekResponse, TaskResponse, TaskCreate, TaskUpdate, RoadmapWeekUpdate
from ..services import roadmap_service
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.goal import Goal
from ..models.roadmap import Roadmap, RoadmapWeek, Task
from ..ai.factory import get_ai_service

router = APIRouter(tags=["roadmap"])

@router.post("/api/goals/{goal_id}/roadmap/generate", response_model=RoadmapResponse)
def generate_roadmap(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Goal not found")

    # Inactivate old roadmaps
    old_roadmaps = db.query(Roadmap).filter(Roadmap.goal_id == goal_id).all()
    for r in old_roadmaps:
        r.is_active = False

    ai_service = get_ai_service()
    goal_info = {
        "name": goal.name,
        "title": goal.title,
        "category": str(goal.category) if goal.category else "",
        "description": goal.description or "",
        "current_level": goal.current_level or "Beginner",
        "target_outcome": goal.target_outcome or "",
        "start_date": goal.start_date,
        "target_date": goal.target_date,
        "available_hours_per_week": goal.available_hours_per_week or 5.0,
        "priority": str(goal.priority) if goal.priority else "medium",
        "preferred_days": goal.preferred_days,
    }
    generated = ai_service.generate_roadmap(goal_info)
    
    roadmap = Roadmap(goal_id=goal_id, version=len(old_roadmaps) + 1, is_active=True)
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    
    for w in generated.weeks:
        week = RoadmapWeek(
            roadmap_id=roadmap.id,
            week_number=w.week_number,
            title=w.title,
            description=w.description,
            start_date=goal.start_date + timedelta(days=7*(w.week_number-1)),
            end_date=goal.start_date + timedelta(days=7*w.week_number - 1),
            estimated_hours=w.estimated_hours
        )
        db.add(week)
        db.commit()
        db.refresh(week)
        
        for t in w.tasks:
            task = Task(
                week_id=week.id,
                title=t.title,
                description=t.description,
                estimated_hours=t.estimated_hours,
                order=t.order
            )
            db.add(task)
            
    db.commit()
    db.refresh(roadmap)
    return roadmap

@router.get("/api/goals/{goal_id}/roadmap", response_model=RoadmapResponse)
def get_roadmap(goal_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return roadmap_service.get_active_roadmap(db, goal_id, current_user)

@router.put("/api/roadmap/weeks/{week_id}", response_model=RoadmapWeekResponse)
def update_week(week_id: uuid.UUID, week_update: RoadmapWeekUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return roadmap_service.update_week(db, week_id, week_update, current_user)

@router.put("/api/roadmap/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: uuid.UUID, task_update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return roadmap_service.update_task(db, task_id, task_update, current_user)

@router.post("/api/roadmap/tasks/{week_id}", response_model=TaskResponse)
def add_task(week_id: uuid.UUID, task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return roadmap_service.add_task(db, week_id, task_data, current_user)

@router.delete("/api/roadmap/tasks/{task_id}")
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return roadmap_service.delete_task(db, task_id, current_user)
