from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Date, Float, Enum, Text, JSON
from sqlalchemy import ForeignKey, func
import uuid
from typing import List, Optional
import enum
from datetime import date, datetime

from ..database import Base


class GoalCategory(str, enum.Enum):
    academics = "academics"
    coding = "coding"
    fitness = "fitness"
    career = "career"
    personal_development = "personal_development"
    other = "other"


class GoalPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class GoalStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"
    cancelled = "cancelled"


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[GoalCategory] = mapped_column(
        Enum(GoalCategory, native_enum=False),
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    current_level: Mapped[str] = mapped_column(String(100), nullable=False)
    target_outcome: Mapped[str] = mapped_column(Text, nullable=False)
    available_hours_per_week: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[GoalPriority] = mapped_column(
        Enum(GoalPriority, native_enum=False),
        default=GoalPriority.medium,
        nullable=False
    )
    motivation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preferred_days: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # List of day names
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, native_enum=False),
        default=GoalStatus.active,
        nullable=False,
        index=True
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

    user = relationship("User", back_populates="goals")
    roadmaps = relationship("Roadmap", back_populates="goal", cascade="all, delete-orphan", passive_deletes=True)
    checkins = relationship("WeeklyCheckin", back_populates="goal", cascade="all, delete-orphan", passive_deletes=True)
    progress_records = relationship("ProgressRecord", back_populates="goal", cascade="all, delete-orphan", passive_deletes=True)
    ai_analyses = relationship("AIAnalysis", back_populates="goal", cascade="all, delete-orphan", passive_deletes=True)
