from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Float, JSON
from sqlalchemy import ForeignKey, func
import uuid
from datetime import datetime
from typing import Optional

from ..database import Base


class UserPreferences(Base):
    """
    User Preferences table:
    Stores user-specific scheduling, timezone, and notification settings independently from core auth.
    """
    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False
    )
    preferred_days: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # List of days e.g. ["Monday", "Wednesday"]
    preferred_study_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC", nullable=False)
    notification_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

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

    user = relationship("User", back_populates="preferences")
