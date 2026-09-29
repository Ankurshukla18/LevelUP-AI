from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Date, Float, Enum, Text, JSON
from sqlalchemy import ForeignKey, func
import uuid
from typing import List, Optional
import enum
from datetime import date

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
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    category: Mapped[GoalCategory] = mapped_column(Enum(GoalCategory))
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date)
    target_date: Mapped[date] = mapped_column(Date)
    current_level: Mapped[str] = mapped_column(String)
    target_outcome: Mapped[str] = mapped_column(Text)
    available_hours_per_week: Mapped[float] = mapped_column(Float)
    priority: Mapped[GoalPriority] = mapped_column(Enum(GoalPriority), default=GoalPriority.medium)
    motivation: Mapped[Optional[str]] = mapped_column(Text)
    preferred_days: Mapped[Optional[dict]] = mapped_column(JSON) # List of day names
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.active)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="goals")
    roadmaps = relationship("Roadmap", back_populates="goal", cascade="all, delete-orphan")
    checkins = relationship("WeeklyCheckin", back_populates="goal", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="goal", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="goal", cascade="all, delete-orphan")
