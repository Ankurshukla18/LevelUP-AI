from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List
import uuid
from datetime import date

from ..models.progress import ProgressRecord


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_goal(self, goal_id: uuid.UUID) -> List[ProgressRecord]:
        return list(
            self.db.execute(
                select(ProgressRecord)
                .where(ProgressRecord.goal_id == goal_id)
                .order_by(ProgressRecord.week_number.asc())
            ).scalars().all()
        )

    def get_latest_for_goal(self, goal_id: uuid.UUID) -> Optional[ProgressRecord]:
        return self.db.execute(
            select(ProgressRecord)
            .where(ProgressRecord.goal_id == goal_id)
            .order_by(ProgressRecord.week_number.desc())
        ).scalars().first()

    def record_progress(
        self,
        goal_id: uuid.UUID,
        user_id: Optional[uuid.UUID],
        week_number: int,
        task_completion_pct: float,
        time_completion_pct: float,
        consistency_pct: float,
        completed_tasks: int,
        total_tasks: int,
        total_hours: float,
        streak_days: int,
        recorded_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> ProgressRecord:
        record = self.db.execute(
            select(ProgressRecord).where(
                ProgressRecord.goal_id == goal_id,
                ProgressRecord.week_number == week_number
            )
        ).scalar_one_or_none()

        if record:
            record.task_completion_pct = task_completion_pct
            record.time_completion_pct = time_completion_pct
            record.consistency_pct = consistency_pct
            record.completed_tasks = completed_tasks
            record.total_tasks = total_tasks
            record.total_hours = total_hours
            record.streak_days = streak_days
            record.progress_percentage = consistency_pct
            record.notes = notes
        else:
            record = ProgressRecord(
                goal_id=goal_id,
                user_id=user_id,
                week_number=week_number,
                task_completion_pct=task_completion_pct,
                time_completion_pct=time_completion_pct,
                consistency_pct=consistency_pct,
                progress_percentage=consistency_pct,
                completed_tasks=completed_tasks,
                total_tasks=total_tasks,
                total_hours=total_hours,
                streak_days=streak_days,
                notes=notes,
            )
            if recorded_date:
                record.recorded_date = recorded_date
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)
        return record
