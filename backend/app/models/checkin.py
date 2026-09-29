from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Float, Enum, Text, Boolean, Integer, JSON
from sqlalchemy import ForeignKey, func, UniqueConstraint, Index
import uuid
from typing import Optional, List
import enum
from datetime import datetime

from ..database import Base


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    moderate = "moderate"
    hard = "hard"
    very_hard = "very_hard"


class WeeklyCheckin(Base):
    __tablename__ = "weekly_checkins"
    __table_args__ = (
        Index("ix_weekly_checkins_goal_week", "goal_id", "week_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    week_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmap_weeks.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    hours_spent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tasks_completed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tasks_skipped: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # JSON array of task names
    accomplishments: Mapped[str] = mapped_column(Text, nullable=False)
    problems_faced: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, native_enum=False),
        nullable=False
    )
    self_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    goal = relationship("Goal", back_populates="checkins")
    week = relationship("RoadmapWeek", back_populates="checkins")
    checkin_tasks = relationship(
        "CheckinTask",
        back_populates="checkin",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    ai_analyses = relationship(
        "AIAnalysis",
        back_populates="checkin",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class CheckinTask(Base):
    __tablename__ = "checkin_tasks"
    __table_args__ = (
        UniqueConstraint("checkin_id", "task_id", name="uq_checkin_task"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    checkin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weekly_checkins.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    checkin = relationship("WeeklyCheckin", back_populates="checkin_tasks")
    task = relationship("Task", back_populates="checkin_tasks")
