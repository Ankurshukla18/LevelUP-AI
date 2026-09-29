from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, model_validator
import uuid
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[EmailStr] = None
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def set_email_from_username(cls, v, info):
        """Accept either 'email' or 'username' field for login compatibility."""
        if v is None:
            username = info.data.get("username")
            if username:
                return username
        return v

    def get_email(self) -> str:
        return self.email or self.username or ""


class GoogleAuthRequest(BaseModel):
    email: EmailStr
    name: str
    oauth_id: str
    avatar_url: Optional[str] = None


class GoogleCallbackRequest(BaseModel):
    code: Optional[str] = None
    state: Optional[str] = None
    redirect_uri: Optional[str] = None
    # Support mock/direct test payload when testing without external Google keys
    mock_email: Optional[EmailStr] = None
    mock_name: Optional[str] = None
    mock_oauth_id: Optional[str] = None
    mock_avatar: Optional[str] = None


class CreateFirstPasswordRequest(BaseModel):
    password: str = Field(min_length=6, max_length=128)
    confirm_password: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


class SetPasswordRequest(BaseModel):
    password: str = Field(min_length=6, max_length=128)


class UserResponse(UserBase):
    id: uuid.UUID
    is_verified: bool = False
    has_password: bool = False
    oauth_provider: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def compute_has_password(cls, data):
        has_pw = False
        if hasattr(data, "hashed_password"):
            has_pw = bool(data.hashed_password)
            data.has_password = has_pw
        elif isinstance(data, dict):
            has_pw = bool(data.get("hashed_password") or data.get("has_password"))
            data["has_password"] = has_pw
        return data


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    requires_password_setup: bool = False
    user: UserResponse
