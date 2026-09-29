from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List, Tuple
import uuid

from ..models.checkin import WeeklyCheckin, CheckinTask


class CheckinRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_by_goal(
        self,
        goal_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[WeeklyCheckin], int]:
        total = self.db.execute(
            select(func.count(WeeklyCheckin.id)).where(WeeklyCheckin.goal_id == goal_id)
        ).scalar_one()

        checkins = self.db.execute(
            select(WeeklyCheckin)
            .where(WeeklyCheckin.goal_id == goal_id)
            .order_by(WeeklyCheckin.created_at.desc())
            .offset(skip)
            .limit(limit)
        ).scalars().all()

        return list(checkins), total

    def get_by_id(self, checkin_id: uuid.UUID) -> Optional[WeeklyCheckin]:
        return self.db.execute(
            select(WeeklyCheckin).where(WeeklyCheckin.id == checkin_id)
        ).scalar_one_or_none()

    def create_checkin_atomic(
        self,
        checkin: WeeklyCheckin,
        checkin_tasks_data: Optional[List[dict]] = None,
    ) -> WeeklyCheckin:
        try:
            self.db.add(checkin)
            self.db.flush()

            if checkin_tasks_data:
                for ct in checkin_tasks_data:
                    task_entry = CheckinTask(
                        checkin_id=checkin.id,
                        task_id=ct["task_id"],
                        status=ct.get("status", "completed"),
                        hours_spent=ct.get("hours_spent", 0.0),
                        is_completed=ct.get("is_completed", True),
                        notes=ct.get("notes"),
                    )
                    self.db.add(task_entry)

            self.db.commit()
            self.db.refresh(checkin)
            return checkin
        except Exception as e:
            self.db.rollback()
            raise e
