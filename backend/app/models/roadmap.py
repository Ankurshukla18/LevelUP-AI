from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Date, Float, Enum, Text, Boolean, Integer
from sqlalchemy import ForeignKey, func, UniqueConstraint, Index
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
    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
        order_by="Task.order",
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
        Index("ix_tasks_week_order", "week_id", "order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    week_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmap_weeks.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
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
    checkin_tasks = relationship(
        "CheckinTask",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
