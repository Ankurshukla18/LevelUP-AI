from sqlalchemy.orm import Session
import uuid
from ..models.progress import ProgressRecord
from ..models.roadmap import RoadmapWeek
from ..models.checkin import WeeklyCheckin
from ..models.goal import Goal

def calculate_and_save_progress(db: Session, goal_id: uuid.UUID, checkin_id: uuid.UUID) -> ProgressRecord:
    checkin = db.query(WeeklyCheckin).filter(WeeklyCheckin.id == checkin_id).first()
    week = db.query(RoadmapWeek).filter(RoadmapWeek.id == checkin.week_id).first()
    
    total_week_tasks = len(week.tasks)
    completed_tasks = checkin.tasks_completed_count
    
    # Do these in Python, NOT via AI
    task_completion_pct = (completed_tasks / total_week_tasks * 100) if total_week_tasks > 0 else 100.0
    
    planned_hours = week.estimated_hours
    actual_hours = checkin.hours_spent
    time_completion_pct = (actual_hours / planned_hours * 100) if planned_hours > 0 else 100.0
    
    # Consistency - simplistic representation based on self rating and task completion
    consistency_pct = (task_completion_pct + time_completion_pct) / 2
    if consistency_pct > 100:
        consistency_pct = 100.0
        
    # Streak calculation
    previous_records = db.query(ProgressRecord).filter(
        ProgressRecord.goal_id == goal_id
    ).order_by(ProgressRecord.created_at.desc()).all()
    
    streak = 1
    if previous_records:
        streak = previous_records[0].streak + 1
        
    delayed_tasks = total_week_tasks - completed_tasks
    
    record = ProgressRecord(
        goal_id=goal_id,
        week_number=week.week_number,
        task_completion_pct=task_completion_pct,
        time_completion_pct=time_completion_pct,
        consistency_pct=consistency_pct,
        total_completed_tasks=completed_tasks,
        total_delayed_tasks=delayed_tasks,
        total_hours=actual_hours,
        streak=streak
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record
