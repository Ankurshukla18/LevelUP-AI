from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List, Tuple
import uuid
from datetime import datetime, timezone

from ..models.goal import Goal, GoalCategory, GoalStatus


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_user(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Goal]:
        """Fetch goal strictly scoped to the authenticated user to prevent unauthorized horizontal access."""
        return self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        ).scalar_one_or_none()

    def list_by_user(
        self,
        user_id: uuid.UUID,
        category: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Goal], int]:
        """Paginated list of goals scoped to user with total count."""
        query = select(Goal).where(Goal.user_id == user_id)
        count_query = select(func.count(Goal.id)).where(Goal.user_id == user_id)

        if category:
            query = query.where(Goal.category == category)
            count_query = count_query.where(Goal.category == category)

        if status:
            query = query.where(Goal.status == status)
            count_query = count_query.where(Goal.status == status)

        total = self.db.execute(count_query).scalar_one()
        goals = self.db.execute(
            query.order_by(Goal.created_at.desc()).offset(skip).limit(limit)
        ).scalars().all()

        return list(goals), total

    def create(self, goal: Goal) -> Goal:
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def update(self, goal: Goal) -> Goal:
        goal.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: Goal) -> None:
        self.db.delete(goal)
        self.db.commit()
