from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..models.goal import Goal
from ..models.checkin import WeeklyCheckin
from ..models.progress import ProgressRecord
from ..models.analysis import AIAnalysis, RoadmapAdjustment
from typing import Optional
from ..models.roadmap import Roadmap, RoadmapWeek, Task
from ..ai.factory import get_ai_service
from ..ai.base import AIProvider
from ..schemas.analysis import AIAnalysisResponse, RoadmapAdjustmentResponse
from ..config import settings
from pydantic import BaseModel, Field, AliasChoices, ConfigDict

router = APIRouter(prefix="/api/goals", tags=["ai"])


def _get_ai_service() -> AIProvider:
    return get_ai_service()


class AnalyzeRequest(BaseModel):
    checkin_id: uuid.UUID = Field(validation_alias=AliasChoices("checkin_id", "checkinId"))

    model_config = ConfigDict(populate_by_name=True)


@router.post("/{goal_id}/analyze", response_model=AIAnalysisResponse)
def analyze_week(
    goal_id: uuid.UUID,
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --- Ownership check ---
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    checkin = db.query(WeeklyCheckin).filter(
        WeeklyCheckin.id == req.checkin_id,
        WeeklyCheckin.goal_id == goal_id,
    ).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Checkin not found")

    # --- Fetch roadmap week context (tasks planned for this week) ---
    roadmap_week = db.query(RoadmapWeek).filter(RoadmapWeek.id == checkin.week_id).first()
    week_tasks = (
        db.query(Task).filter(Task.roadmap_week_id == checkin.week_id).order_by(Task.order_index).all()
        if roadmap_week else []
    )

    # --- Fetch the most recent progress snapshot for this checkin week ---
    progress = (
        db.query(ProgressRecord)
        .filter(ProgressRecord.goal_id == goal_id)
        .order_by(ProgressRecord.created_at.desc())
        .first()
    )

    # --- Fetch previous checkin for context (if any) ---
    previous_checkin = (
        db.query(WeeklyCheckin)
        .filter(
            WeeklyCheckin.goal_id == goal_id,
            WeeklyCheckin.id != checkin.id,
        )
        .order_by(WeeklyCheckin.created_at.desc())
        .first()
    )

    # --- Build rich checkin payload for OpenAI ---
    planned_tasks_count = len(week_tasks)
    task_completion_pct = progress.task_completion_pct if progress else (
        round(checkin.completed_tasks / max(checkin.planned_tasks, 1) * 100, 1)
        if checkin.planned_tasks else 0.0
    )
    time_completion_pct = progress.time_completion_pct if progress else (
        round(checkin.actual_hours / max(checkin.planned_hours, 0.01) * 100, 1)
        if checkin.planned_hours else 0.0
    )
    consistency_pct = progress.consistency_percentage if progress else (
        round(checkin.work_days_completed / max(checkin.work_days_planned, 1) * 100, 1)
        if checkin.work_days_planned else 0.0
    )

    checkin_data = {
        "week_number": roadmap_week.week_number if roadmap_week else None,
        "week_title": roadmap_week.title if roadmap_week else None,
        "planned_hours": checkin.planned_hours,
        "planned_tasks_count": planned_tasks_count,
        "tasks": [{"title": t.title, "description": t.description} for t in week_tasks],
        "hours_spent": checkin.actual_hours,
        "accomplishments": checkin.accomplishments,
        "problems_faced": checkin.problems,
        "difficulty_level": checkin.difficulty,
        "self_rating": checkin.self_rating,
        "notes": checkin.notes,
        "previous_context": (
            {
                "hours_spent": previous_checkin.actual_hours,
                "self_rating": previous_checkin.self_rating,
                "accomplishments": previous_checkin.accomplishments,
            }
            if previous_checkin else None
        ),
    }

    goal_info = {
        "name": goal.name,
        "category": str(goal.category) if goal.category else "",
        "target_outcome": goal.target_outcome or "",
        "available_hours_per_week": goal.available_hours_per_week or 5.0,
    }

    progress_data = {
        "task_completion_pct": task_completion_pct,
        "time_completion_pct": time_completion_pct,
        "consistency_pct": consistency_pct,
        "completed_tasks": checkin.completed_tasks,
        "delayed_tasks": checkin.delayed_tasks,
        "streak": progress.streak_days if progress else 0,
    }

    # --- Call OpenAI (raises AIServiceException on failure) ---
    ai_service = _get_ai_service()
    analysis_res = ai_service.analyze_week(
        checkin_data=checkin_data,
        goal_info=goal_info,
        progress=progress_data,
    )

    # --- Persist analysis result ---
    analysis = AIAnalysis(
        checkin_id=checkin.id,
        goal_id=goal_id,
        summary=analysis_res.summary,
        went_well=analysis_res.went_well,
        delayed=analysis_res.delayed,
        reasons=analysis_res.reasons,
        recommendations=analysis_res.recommendations,
        next_week_focus=analysis_res.next_week_focus,
        roadmap_adjustment_type=analysis_res.roadmap_adjustment_type,
        adjustment_details=analysis_res.adjustment_details,
        model_name=getattr(ai_service, "model", None) or settings.OPENAI_MODEL or "gpt-4o",
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


class AdjustRequest(BaseModel):
    analysis_id: uuid.UUID = Field(validation_alias=AliasChoices("analysis_id", "analysisId"))
    roadmap_id: Optional[uuid.UUID] = Field(default=None, validation_alias=AliasChoices("roadmap_id", "roadmapId"))

    model_config = ConfigDict(populate_by_name=True)


@router.post("/{goal_id}/roadmap/adjust", response_model=RoadmapAdjustmentResponse)
def adjust_roadmap(
    goal_id: uuid.UUID,
    req: AdjustRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.id == req.analysis_id,
        AIAnalysis.goal_id == goal_id,
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    target_roadmap_id = req.roadmap_id
    if not target_roadmap_id:
        active_roadmap = db.query(Roadmap).filter(Roadmap.goal_id == goal_id, Roadmap.is_active == True).first()
        if not active_roadmap:
            active_roadmap = db.query(Roadmap).filter(Roadmap.goal_id == goal_id).order_by(Roadmap.created_at.desc()).first()
        if not active_roadmap:
            raise HTTPException(status_code=404, detail="No roadmap found for this goal to adjust")
        target_roadmap_id = active_roadmap.id

    ai_service = _get_ai_service()
    suggestion = ai_service.suggest_adjustment(
        analysis={
            "roadmap_adjustment_type": analysis.roadmap_adjustment_type,
            "adjustment_details": analysis.adjustment_details,
        },
        roadmap={"id": str(target_roadmap_id)},
        remaining_weeks=4,
    )

    reason_text = getattr(suggestion, "reason", None) or "Weekly progress adaptation suggested by AI"
    adjustment = RoadmapAdjustment(
        roadmap_id=target_roadmap_id,
        analysis_id=req.analysis_id,
        adjustment_type=suggestion.adjustment_type,
        details=suggestion.details,
        reason=reason_text,
        status="applied",
    )
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    return adjustment


@router.post("/{goal_id}/monthly-review")
def monthly_review(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == current_user.id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    checkins = (
        db.query(WeeklyCheckin)
        .filter(WeeklyCheckin.goal_id == goal_id)
        .order_by(WeeklyCheckin.created_at.asc())
        .all()
    )
    records = (
        db.query(ProgressRecord)
        .filter(ProgressRecord.goal_id == goal_id)
        .order_by(ProgressRecord.week_number.asc())
        .all()
    )

    goal_data = {
        "name": goal.name,
        "category": str(goal.category) if goal.category else "",
        "target_outcome": goal.target_outcome or "",
    }

    checkin_dicts = [
        {
            "week_id": str(c.week_id),
            "hours_spent": c.actual_hours,
            "completed_tasks": c.completed_tasks,
            "delayed_tasks": c.delayed_tasks,
            "self_rating": c.self_rating,
            "accomplishments": c.accomplishments,
            "problems": c.problems or "",
            "difficulty": c.difficulty,
        }
        for c in checkins
    ]

    progress_dicts = [
        {
            "week_number": r.week_number,
            "task_completion_pct": r.task_completion_pct,
            "time_completion_pct": r.time_completion_pct,
            "consistency_pct": r.consistency_percentage,
        }
        for r in records
    ]

    ai_service = _get_ai_service()
    summary = ai_service.generate_monthly_summary(
        goal=goal_data,
        checkins=checkin_dicts,
        progress_records=progress_dicts,
    )

    return summary.model_dump()
