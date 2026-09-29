from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
import uuid
from datetime import datetime, timezone

from ..models.user import User
from ..models.user_preferences import UserPreferences


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.execute(select(User).where(User.email == email.lower().strip())).scalar_one_or_none()

    def get_by_google_id(self, google_id: str) -> Optional[User]:
        return self.db.execute(select(User).where(User.google_id == google_id)).scalar_one_or_none()

    def create(
        self,
        name: str,
        email: str,
        password_hash: Optional[str] = None,
        google_id: Optional[str] = None,
        profile_picture: Optional[str] = None,
        auth_provider: str = "local",
        email_verified: bool = False,
    ) -> User:
        user = User(
            name=name,
            email=email.lower().strip(),
            password_hash=password_hash,
            google_id=google_id,
            profile_picture=profile_picture,
            auth_provider=auth_provider,
            email_verified=email_verified,
            is_active=True,
            last_login_at=datetime.now(timezone.utc),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        user.reset_password_token = None
        user.reset_password_token_expires_at = None
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

    def get_or_create_preferences(self, user_id: uuid.UUID) -> UserPreferences:
        prefs = self.db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        ).scalar_one_or_none()
        if not prefs:
            prefs = UserPreferences(user_id=user_id, timezone="UTC")
            self.db.add(prefs)
            self.db.commit()
            self.db.refresh(prefs)
        return prefs
