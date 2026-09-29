from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import func
import uuid
from datetime import datetime
from typing import List, Optional

from ..database import Base


class User(Base):
    """
    User model supporting:
    - Standard Email/Password authentication
    - Google OAuth authentication (oauth_provider, oauth_id)
    - Hybrid accounts (Google OAuth users who later set a password)
    - Email verification status (is_verified, verification_token)
    - Password reset functionality (reset_password_token)
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Nullable for OAuth-only users, populated for email/password or when Google users set password
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # OAuth fields
    oauth_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    oauth_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Email verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Password reset
    reset_password_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    reset_password_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    goals: Mapped[List["Goal"]] = relationship(
        "Goal",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
