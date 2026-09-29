from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Float, Integer
from sqlalchemy import ForeignKey, func, UniqueConstraint, Index
import uuid
from datetime import datetime

from ..database import Base


class ProgressRecord(Base):
    __tablename__ = "progress_records"
    __table_args__ = (
        UniqueConstraint("goal_id", "week_number", name="uq_progress_goal_week"),
        Index("ix_progress_records_goal_week", "goal_id", "week_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    task_completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    time_completion_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    consistency_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_completed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_delayed_tasks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    streak: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    goal = relationship("Goal", back_populates="progress_records")
