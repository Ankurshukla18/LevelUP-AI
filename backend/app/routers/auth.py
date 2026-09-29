from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenWithUser,
    GoogleCallbackRequest,
    CreateFirstPasswordRequest,
    VerifyEmailRequest,
    SetPasswordRequest,
)
from ..services import auth_service
from ..dependencies.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email and password."""
    return auth_service.register_user(db, user)


@router.post("/login", response_model=TokenWithUser)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user with email and password and return a JWT access token."""
    return auth_service.authenticate_user(db, user)


@router.get("/google/url")
def get_google_auth_url():
    """
    Get Google OAuth 2.0 Authorization URL.
    Secrets are kept strictly in backend environment variables.
    """
    return auth_service.get_google_authorization_url()


@router.post("/google/callback", response_model=TokenWithUser)
def google_callback(req: GoogleCallbackRequest, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback:
    - Automatically creates user in PostgreSQL users table if new
    - Seamlessly links to existing account if email already exists
    - Sets requires_password_setup = True for new Google users without a password
    - Sets requires_password_setup = False if user already configured a password
    """
    return auth_service.process_google_callback(db, req)


@router.post("/create-password", response_model=TokenWithUser)
def create_first_password(
    req: CreateFirstPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mandatory password creation endpoint for new Google users.
    Once created, the user can log in with either Google or email + password.
    """
    return auth_service.create_first_password(db, current_user, req)


@router.post("/set-password")
def set_password(
    req: SetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allows an authenticated user to update their password."""
    return auth_service.set_user_password(db, current_user, req.password)


@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify user email address using verification token."""
    return auth_service.verify_email(db, req.token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get profile of current authenticated user."""
    return current_user
