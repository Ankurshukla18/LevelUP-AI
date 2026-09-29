from sqlalchemy.orm import Session
from ..models.user import User
from ..models.goal import Goal, GoalStatus
from ..models.progress import ProgressRecord
from collections import defaultdict

def get_dashboard_analytics(db: Session, user: User) -> dict:
    goals = db.query(Goal).filter(Goal.user_id == user.id).all()
    
    active_goals = [g for g in goals if g.status == GoalStatus.active]
    completed_goals = [g for g in goals if g.status == GoalStatus.completed]
    
    goals_by_category = defaultdict(int)
    for g in goals:
        goals_by_category[g.category.value if hasattr(g.category, 'value') else str(g.category)] += 1
        
    goal_ids = [g.id for g in goals]
    progress_records = db.query(ProgressRecord).filter(ProgressRecord.goal_id.in_(goal_ids)).order_by(ProgressRecord.created_at.desc()).limit(10).all()
    
    total_hours = sum(pr.total_hours for pr in progress_records)
    
    overall_completion = 0.0
    if progress_records:
        overall_completion = sum(pr.task_completion_pct for pr in progress_records) / len(progress_records)
        
    current_streak = 0
    if progress_records:
        current_streak = max([pr.streak for pr in progress_records])
        
    weekly_completion_pct = 0.0
    if progress_records:
        weekly_completion_pct = progress_records[0].task_completion_pct
        
    weekly_data = []
    week_map = {}
    for pr in reversed(progress_records[:5]):
        if pr.week_number not in week_map:
            week_map[pr.week_number] = {"task_pct_sum": 0, "time_pct_sum": 0, "count": 0}
        week_map[pr.week_number]["task_pct_sum"] += pr.task_completion_pct
        week_map[pr.week_number]["time_pct_sum"] += pr.time_completion_pct
        week_map[pr.week_number]["count"] += 1
        
    for week, data in sorted(week_map.items()):
        weekly_data.append({
            "week": week,
            "task_pct": data["task_pct_sum"] / data["count"],
            "time_pct": data["time_pct_sum"] / data["count"]
        })
    
    return {
        "active_goals_count": len(active_goals),
        "completed_goals_count": len(completed_goals),
        "overall_completion_pct": overall_completion,
        "total_hours_spent": total_hours,
        "current_streak": current_streak,
        "recent_progress": progress_records,
        "weekly_completion_pct": weekly_completion_pct,
        "goals_by_category": dict(goals_by_category),
        "weekly_progress_data": weekly_data
    }
