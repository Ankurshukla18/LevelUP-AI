from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from ..models.analysis import AIAnalysis, RoadmapAdjustment


class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_analysis(self, analysis: AIAnalysis) -> AIAnalysis:
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def list_by_goal(self, goal_id: uuid.UUID) -> List[AIAnalysis]:
        return list(
            self.db.execute(
                select(AIAnalysis)
                .where(AIAnalysis.goal_id == goal_id)
                .order_by(AIAnalysis.created_at.desc())
            ).scalars().all()
        )

    def create_adjustment_suggestion(self, adjustment: RoadmapAdjustment) -> RoadmapAdjustment:
        """Saves AI suggestion. Status defaults to 'pending' waiting for user approval."""
        self.db.add(adjustment)
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    def update_adjustment_status(
        self,
        adjustment_id: uuid.UUID,
        new_status: str,  # 'approved' | 'rejected' | 'applied'
    ) -> Optional[RoadmapAdjustment]:
        adjustment = self.db.execute(
            select(RoadmapAdjustment).where(RoadmapAdjustment.id == adjustment_id)
        ).scalar_one_or_none()

        if not adjustment:
            return None

        adjustment.status = new_status
        now = datetime.now(timezone.utc)
        if new_status in ("approved", "applied"):
            adjustment.approved_at = now
        elif new_status == "rejected":
            adjustment.rejected_at = now

        adjustment.updated_at = now
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment
