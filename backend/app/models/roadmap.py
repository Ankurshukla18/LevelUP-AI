from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from sqlalchemy.types import String, DateTime, Date, Float, Enum, Text, Boolean, Integer
from sqlalchemy import ForeignKey, func, UniqueConstraint, Index, CheckConstraint
import uuid
from typing import List, Optional
import enum
from datetime import date, datetime

from ..database import Base


class WeekStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    delayed = "delayed"


class Roadmap(Base):
    """
    Roadmaps table supporting versioning and lifecycle states: active, archived, draft.
    Prevents silent destruction of previous roadmaps during AI adjustments.
    """
    __tablename__ = "roadmaps"
    __table_args__ = (
        Index("ix_roadmaps_goal_status", "goal_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), default="Roadmap", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False, index=True)  # active, archived, draft
    generated_by: Mapped[str] = mapped_column(String(50), default="ai", nullable=False)  # ai, user
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
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

    goal = relationship("Goal", back_populates="roadmaps")
    weeks = relationship(
        "RoadmapWeek",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        order_by="RoadmapWeek.week_number",
        passive_deletes=True
    )
    milestones = relationship(
        "Milestone",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    adjustments = relationship(
        "RoadmapAdjustment",
        back_populates="roadmap",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class RoadmapWeek(Base):
    __tablename__ = "roadmap_weeks"
    __table_args__ = (
        UniqueConstraint("roadmap_id", "week_number", name="uq_roadmap_week_number"),
        CheckConstraint("estimated_hours >= 0", name="ck_roadmap_weeks_estimated_hours"),
        Index("ix_roadmap_weeks_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    objective: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description = synonym("objective")

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    estimated_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[WeekStatus] = mapped_column(
        Enum(WeekStatus, native_enum=False),
        default=WeekStatus.not_started,
        nullable=False
    )
    
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

    roadmap = relationship("Roadmap", back_populates="weeks")
    tasks = relationship(
        "Task",
        back_populates="week",
        cascade="all, delete-orphan",
        order_by="Task.order_index",
        passive_deletes=True
    )
    milestones = relationship(
        "Milestone",
        back_populates="week",
        passive_deletes=True
    )
    checkins = relationship(
        "WeeklyCheckin",
        back_populates="week",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("estimated_hours IS NULL OR estimated_hours >= 0", name="ck_tasks_estimated_hours"),
        Index("ix_tasks_week_order", "roadmap_week_id", "order_index"),
        Index("ix_tasks_status", "status"),
        Index("ix_tasks_due_date", "due_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_week_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmap_weeks.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    week_id = synonym("roadmap_week_id")

    milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("milestones.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    priority: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order = synonym("order_index")
    
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

    week = relationship("RoadmapWeek", back_populates="tasks")
    milestone = relationship("Milestone", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    checkin_tasks = relationship(
        "CheckinTask",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
