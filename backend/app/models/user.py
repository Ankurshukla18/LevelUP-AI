from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from sqlalchemy.types import String, DateTime, Boolean
from sqlalchemy import func
import uuid
from datetime import datetime
from typing import List, Optional

from ..database import Base


class User(Base):
    """
    User model supporting:
    - Standard Email + Password authentication
    - Google OAuth 2.0 / OpenID Connect (google_id, profile_picture, auth_provider)
    - Hybrid accounts (Google OAuth users who later create a password)
    - Email verification status (email_verified, verification_token)
    - Password reset functionality (reset_password_token)
    - User preferences and activity tracking (is_active, last_login_at)
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # Nullable for OAuth-only users before password setup, populated when password is set
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hashed_password = synonym("password_hash")

    # OAuth fields
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    oauth_id = synonym("google_id")

    profile_picture: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    avatar_url = synonym("profile_picture")

    auth_provider: Mapped[str] = mapped_column(String(50), default="local", nullable=False, index=True)
    oauth_provider = synonym("auth_provider")

    # Status & Activity
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified = synonym("email_verified")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Verification & Reset tokens
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    verification_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

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
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
