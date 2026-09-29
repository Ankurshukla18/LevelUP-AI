from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Float, Enum, Text, Boolean, Integer, JSON
from sqlalchemy import ForeignKey, func
import uuid
from typing import Optional, List
import enum

from ..database import Base

class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    moderate = "moderate"
    hard = "hard"
    very_hard = "very_hard"

class WeeklyCheckin(Base):
    __tablename__ = "weekly_checkins"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id"))
    week_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmap_weeks.id"))
    hours_spent: Mapped[float] = mapped_column(Float)
    tasks_completed_count: Mapped[int] = mapped_column(Integer)
    tasks_skipped: Mapped[Optional[dict]] = mapped_column(JSON) # JSON array of task names
    accomplishments: Mapped[str] = mapped_column(Text)
    problems_faced: Mapped[Optional[str]] = mapped_column(Text)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(Enum(DifficultyLevel))
    self_rating: Mapped[int] = mapped_column(Integer) # 1-10
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    goal = relationship("Goal", back_populates="checkins")
    week = relationship("RoadmapWeek", back_populates="checkins")
    checkin_tasks = relationship("CheckinTask", back_populates="checkin", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="checkin", cascade="all, delete-orphan")


class CheckinTask(Base):
    __tablename__ = "checkin_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    checkin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("weekly_checkins.id"))
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"))
    is_completed: Mapped[bool] = mapped_column(Boolean)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    checkin = relationship("WeeklyCheckin", back_populates="checkin_tasks")
    task = relationship("Task", back_populates="checkin_tasks")
