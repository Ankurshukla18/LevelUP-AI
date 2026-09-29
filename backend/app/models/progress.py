from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from sqlalchemy.types import DateTime, Date, Float, Integer, Text
from sqlalchemy import ForeignKey, func, UniqueConstraint, Index, CheckConstraint
import uuid
from datetime import date, datetime
from typing import Optional

from ..database import Base


class ProgressRecord(Base):
    """
    Historical progress snapshots for analytics, Recharts visualization, and trend analysis.
    """
    __tablename__ = "progress_records"
    __table_args__ = (
        CheckConstraint("progress_percentage >= 0 AND progress_percentage <= 100", name="ck_progress_percentage"),
        CheckConstraint("consistency_percentage >= 0 AND consistency_percentage <= 100", name="ck_consistency_percentage"),
        CheckConstraint("total_hours >= 0", name="ck_progress_total_hours"),
        Index("ix_progress_records_goal_week", "goal_id", "week_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    recorded_date: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date(),
        nullable=False,
        index=True
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    progress_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    consistency_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    consistency_pct = synonym("consistency_percentage")

    total_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    completed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_completed_tasks = synonym("completed_tasks")

    total_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_delayed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    streak_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak = synonym("streak_days")

    task_completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    goal = relationship("Goal", back_populates="progress_records")
