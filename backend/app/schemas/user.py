from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
import uuid
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[EmailStr] = None
    password: str

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


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
