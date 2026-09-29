from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime, Float, Integer
from sqlalchemy import ForeignKey, func
import uuid

from ..database import Base

class ProgressRecord(Base):
    __tablename__ = "progress_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    goal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("goals.id"))
    week_number: Mapped[int] = mapped_column(Integer)
    task_completion_pct: Mapped[float] = mapped_column(Float)
    time_completion_pct: Mapped[float] = mapped_column(Float)
    consistency_pct: Mapped[float] = mapped_column(Float)
    total_completed_tasks: Mapped[int] = mapped_column(Integer)
    total_delayed_tasks: Mapped[int] = mapped_column(Integer)
    total_hours: Mapped[float] = mapped_column(Float)
    streak: Mapped[int] = mapped_column(Integer)
    
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    goal = relationship("Goal", back_populates="progress_records")
