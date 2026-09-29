from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenWithUser,
    GoogleAuthRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
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


@router.post("/google", response_model=TokenWithUser)
def google_auth(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate or register a user via Google OAuth."""
    return auth_service.authenticate_google_user(db, req)


@router.post("/set-password")
def set_password(
    req: SetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Allows an authenticated user (such as a Google user) to create or update their password."""
    return auth_service.set_user_password(db, current_user, req.password)


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Initiate password reset by requesting a reset token."""
    return auth_service.request_password_reset(db, req.email)


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset user password using a valid reset token."""
    return auth_service.confirm_password_reset(db, req.token, req.new_password)


@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    """Verify user email address using verification token."""
    return auth_service.verify_email(db, req.token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get profile of current authenticated user."""
    return current_user
