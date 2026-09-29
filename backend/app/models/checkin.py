from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from sqlalchemy.types import String, DateTime, Date, Float, Enum, Text, Boolean, Integer, JSON
from sqlalchemy import ForeignKey, func, UniqueConstraint, Index, CheckConstraint
import uuid
from typing import Optional, List
import enum
from datetime import date, datetime

from ..database import Base


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    moderate = "moderate"
    hard = "hard"
    very_hard = "very_hard"


class WeeklyCheckin(Base):
    __tablename__ = "weekly_checkins"
    __table_args__ = (
        CheckConstraint("self_rating >= 1 AND self_rating <= 10", name="ck_weekly_checkin_self_rating"),
        CheckConstraint("actual_hours >= 0", name="ck_weekly_checkin_actual_hours"),
        CheckConstraint("planned_hours >= 0", name="ck_weekly_checkin_planned_hours"),
        Index("ix_weekly_checkins_goal_week", "goal_id", "week_id"),
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
    week_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmap_weeks.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    week_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    week_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    planned_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    actual_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    hours_spent = synonym("actual_hours")

    planned_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tasks_completed_count = synonym("completed_tasks")

    skipped_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delayed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    work_days_planned: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    work_days_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    self_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-10
    accomplishments: Mapped[str] = mapped_column(Text, nullable=False)
    problems: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    problems_faced = synonym("problems")

    difficulty: Mapped[str] = mapped_column(String(50), default="moderate", nullable=False)
    difficulty_level = synonym("difficulty")

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tasks_skipped: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
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
        CheckConstraint("hours_spent >= 0", name="ck_checkin_task_hours_spent"),
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
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    hours_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    checkin = relationship("WeeklyCheckin", back_populates="checkin_tasks")
    task = relationship("Task", back_populates="checkin_tasks")
