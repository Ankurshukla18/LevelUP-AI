from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Date, Float, Enum, Text, Boolean, Integer
from sqlalchemy import ForeignKey, func
import uuid
from typing import List, Optional
import enum
from datetime import date

from ..database import Base

class WeekStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    delayed = "delayed"

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    generated_by_ai: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    goal = relationship("Goal", back_populates="roadmaps")
    weeks = relationship("RoadmapWeek", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapWeek.week_number")
    adjustments = relationship("RoadmapAdjustment", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapWeek(Base):
    __tablename__ = "roadmap_weeks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmaps.id"))
    week_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    estimated_hours: Mapped[float] = mapped_column(Float)
    status: Mapped[WeekStatus] = mapped_column(Enum(WeekStatus), default=WeekStatus.not_started)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    roadmap = relationship("Roadmap", back_populates="weeks")
    tasks = relationship("Task", back_populates="week", cascade="all, delete-orphan", order_by="Task.order")
    checkins = relationship("WeeklyCheckin", back_populates="week", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    week_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmap_weeks.id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    week = relationship("RoadmapWeek", back_populates="tasks")
    checkin_tasks = relationship("CheckinTask", back_populates="task", cascade="all, delete-orphan")
