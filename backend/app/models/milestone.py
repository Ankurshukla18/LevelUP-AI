from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Date, Text
from sqlalchemy import ForeignKey, func, Index
import uuid
from typing import Optional, List
from datetime import date, datetime

from ..database import Base


class Milestone(Base):
    """
    Dedicated Milestones table for milestone tracking independent from individual tasks.
    """
    __tablename__ = "milestones"
    __table_args__ = (
        Index("ix_milestones_roadmap_status", "roadmap_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    week_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("roadmap_weeks.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

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

    roadmap = relationship("Roadmap", back_populates="milestones")
    week = relationship("RoadmapWeek", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone")
