from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
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
    approved = "approved"
    rejected = "rejected"
    applied = "applied"


class AIAnalysis(Base):
    """
    Stores AI-generated analysis, weekly summaries, and recommendations.
    Historical record preserved for student reflection and progress analytics.
    """
    __tablename__ = "ai_analyses"
    __table_args__ = (
        Index("ix_ai_analyses_goal_created", "goal_id", "created_at"),
        Index("ix_ai_analyses_type", "analysis_type"),
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
    checkin_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("weekly_checkins.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    analysis_type: Mapped[str] = mapped_column(String(50), default="weekly_checkin", nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    what_went_well: Mapped[dict] = mapped_column(JSON, nullable=False)
    went_well = synonym("what_went_well")

    delayed_items: Mapped[dict] = mapped_column(JSON, nullable=False)
    delayed = synonym("delayed_items")

    possible_reasons: Mapped[dict] = mapped_column(JSON, nullable=False)
    reasons = synonym("possible_reasons")

    recommendations: Mapped[dict] = mapped_column(JSON, nullable=False)
    next_week_focus: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    roadmap_adjustment_type: Mapped[str] = mapped_column(String(50), default="none", nullable=False)
    roadmap_adjustment_suggestion: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    adjustment_details = synonym("roadmap_adjustment_suggestion")

    model_name: Mapped[str] = mapped_column(String(100), default="mock-ai", nullable=False)
    
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
    """
    Stores AI-suggested roadmap adjustments.
    CRITICAL: AI only SUGGESTS modifications; adjustments are NOT automatically applied.
    User approval is strictly required before status transitions to 'applied'.
    """
    __tablename__ = "roadmap_adjustments"
    __table_args__ = (
        Index("ix_roadmap_adjustments_goal_status", "goal_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    ai_analysis_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ai_analyses.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    analysis_id = synonym("ai_analysis_id")
    reason: Mapped[str] = mapped_column(Text, default="AI-suggested roadmap adjustment", nullable=False)
    changes: Mapped[dict] = mapped_column(JSON, nullable=False)
    details = synonym("changes")

    adjustment_type: Mapped[str] = mapped_column(String(50), default="reduce", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", index=True, nullable=False)  # pending, approved, rejected, applied
    
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

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
    goal = relationship("Goal", back_populates="roadmap_adjustments")
