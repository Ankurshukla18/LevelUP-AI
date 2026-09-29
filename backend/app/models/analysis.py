from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Enum, Text, JSON
from sqlalchemy import ForeignKey, func
import uuid
from typing import Optional
import enum

from ..database import Base

class AdjustmentType(str, enum.Enum):
    none = "none"
    reduce = "reduce"
    extend = "extend"
    reorder = "reorder"

class AdjustmentStatus(str, enum.Enum):
    pending = "pending"
    applied = "applied"
    rejected = "rejected"

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    checkin_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("weekly_checkins.id"))
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id"))
    summary: Mapped[str] = mapped_column(Text)
    went_well: Mapped[dict] = mapped_column(JSON) # list of strings
    delayed: Mapped[dict] = mapped_column(JSON) # list of strings
    reasons: Mapped[dict] = mapped_column(JSON) # list of strings
    recommendations: Mapped[dict] = mapped_column(JSON) # list of strings
    next_week_focus: Mapped[dict] = mapped_column(JSON) # list of strings
    roadmap_adjustment_type: Mapped[AdjustmentType] = mapped_column(Enum(AdjustmentType))
    adjustment_details: Mapped[Optional[dict]] = mapped_column(JSON)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    checkin = relationship("WeeklyCheckin", back_populates="ai_analyses")
    goal = relationship("Goal", back_populates="ai_analyses")
    roadmap_adjustments = relationship("RoadmapAdjustment", back_populates="analysis", cascade="all, delete-orphan")


class RoadmapAdjustment(Base):
    __tablename__ = "roadmap_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roadmaps.id"))
    analysis_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_analyses.id"))
    adjustment_type: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSON)
    status: Mapped[AdjustmentStatus] = mapped_column(Enum(AdjustmentStatus), default=AdjustmentStatus.pending)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    roadmap = relationship("Roadmap", back_populates="adjustments")
    analysis = relationship("AIAnalysis", back_populates="roadmap_adjustments")
