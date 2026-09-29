from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import Optional, List
import uuid

from ..models.roadmap import Roadmap, RoadmapWeek, Task
from ..models.milestone import Milestone


class RoadmapRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_roadmap(self, goal_id: uuid.UUID) -> Optional[Roadmap]:
        return self.db.execute(
            select(Roadmap).where(
                Roadmap.goal_id == goal_id,
                Roadmap.is_active == True,
                Roadmap.status == "active"
            )
        ).scalar_one_or_none()

    def list_roadmaps(self, goal_id: uuid.UUID) -> List[Roadmap]:
        return list(
            self.db.execute(
                select(Roadmap).where(Roadmap.goal_id == goal_id).order_by(Roadmap.version.desc())
            ).scalars().all()
        )

    def archive_active_roadmaps(self, goal_id: uuid.UUID) -> None:
        """Archive existing active roadmaps before activating a new version without destroying historical data."""
        self.db.execute(
            update(Roadmap)
            .where(Roadmap.goal_id == goal_id, Roadmap.is_active == True)
            .values(is_active=False, status="archived")
        )

    def create_roadmap_atomic(
        self,
        goal_id: uuid.UUID,
        version: int,
        title: str,
        weeks_data: List[dict],
        milestones_data: Optional[List[dict]] = None,
    ) -> Roadmap:
        """
        Creates roadmap, weeks, tasks, and milestones in a single atomic transaction.
        If any step fails, the entire transaction is rolled back.
        """
        try:
            # 1. Archive prior active versions
            self.archive_active_roadmaps(goal_id)

            # 2. Create new active roadmap
            roadmap = Roadmap(
                goal_id=goal_id,
                title=title,
                version=version,
                status="active",
                is_active=True,
                generated_by="ai",
                generated_by_ai=True,
            )
            self.db.add(roadmap)
            self.db.flush()  # Assigns roadmap.id

            # 3. Create weeks and their tasks
            for w in weeks_data:
                week = RoadmapWeek(
                    roadmap_id=roadmap.id,
                    week_number=w["week_number"],
                    title=w["title"],
                    objective=w.get("description") or w.get("objective"),
                    start_date=w["start_date"],
                    end_date=w["end_date"],
                    estimated_hours=w.get("estimated_hours", 0.0),
                    status=w.get("status", "not_started"),
                )
                self.db.add(week)
                self.db.flush()

                for order, t in enumerate(w.get("tasks", []), start=1):
                    task = Task(
                        roadmap_week_id=week.id,
                        goal_id=goal_id,
                        title=t["title"],
                        description=t.get("description"),
                        estimated_hours=t.get("estimated_hours", 1.0),
                        priority=t.get("priority", "medium"),
                        status=t.get("status", "pending"),
                        is_completed=t.get("is_completed", False),
                        order_index=t.get("order") or order,
                    )
                    self.db.add(task)

            # 4. Optional milestones
            if milestones_data:
                for m in milestones_data:
                    milestone = Milestone(
                        roadmap_id=roadmap.id,
                        title=m["title"],
                        description=m.get("description"),
                        target_date=m.get("target_date"),
                        status=m.get("status", "pending"),
                    )
                    self.db.add(milestone)

            self.db.commit()
            self.db.refresh(roadmap)
            return roadmap

        except Exception as e:
            self.db.rollback()
            raise e
