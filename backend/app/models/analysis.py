from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Enum, Text, JSON
from sqlalchemy import ForeignKey, func, Index
import uuid
from typing import Optional
import enum
from datetime import datetime

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
    __table_args__ = (
        Index("ix_ai_analyses_goal_created", "goal_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    checkin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weekly_checkins.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    went_well: Mapped[dict] = mapped_column(JSON, nullable=False)  # list of strings
    delayed: Mapped[dict] = mapped_column(JSON, nullable=False)    # list of strings
    reasons: Mapped[dict] = mapped_column(JSON, nullable=False)    # list of strings
    recommendations: Mapped[dict] = mapped_column(JSON, nullable=False)  # list of strings
    next_week_focus: Mapped[dict] = mapped_column(JSON, nullable=False)  # list of strings
    roadmap_adjustment_type: Mapped[AdjustmentType] = mapped_column(
        Enum(AdjustmentType, native_enum=False),
        default=AdjustmentType.none,
        nullable=False
    )
    adjustment_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    checkin = relationship("WeeklyCheckin", back_populates="ai_analyses")
    goal = relationship("Goal", back_populates="ai_analyses")
    roadmap_adjustments = relationship(
        "RoadmapAdjustment",
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class RoadmapAdjustment(Base):
    __tablename__ = "roadmap_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    adjustment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[AdjustmentStatus] = mapped_column(
        Enum(AdjustmentStatus, native_enum=False),
        default=AdjustmentStatus.pending,
        index=True,
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

    roadmap = relationship("Roadmap", back_populates="adjustments")
    analysis = relationship("AIAnalysis", back_populates="roadmap_adjustments")
