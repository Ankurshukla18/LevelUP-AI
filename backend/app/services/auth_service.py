import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..schemas.user import UserCreate, UserLogin, GoogleAuthRequest, SetPasswordRequest
from ..models.user import User
from ..utils.security import get_password_hash, verify_password, create_access_token


def register_user(db: Session, user: UserCreate) -> User:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    verification_token = secrets.token_urlsafe(32)
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires_at=datetime.now(timezone.utc) + timedelta(days=2),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, user: UserLogin) -> dict:
    email = user.get_email()
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # If user registered via Google OAuth and hasn't created a password yet
    if not db_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was created with Google Sign-In. Please sign in with Google or use Set Password.",
        )

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user,
    }


def authenticate_google_user(db: Session, req: GoogleAuthRequest) -> dict:
    """
    Authenticate or register a user via Google OAuth.
    If the user already exists (by email), links the Google account.
    If the user is new, creates an account with verified email.
    """
    db_user = db.query(User).filter(User.email == req.email).first()
    if db_user:
        # Link Google account if not linked
        if not db_user.oauth_id:
            db_user.oauth_provider = "google"
            db_user.oauth_id = req.oauth_id
        if req.avatar_url and not db_user.avatar_url:
            db_user.avatar_url = req.avatar_url
        db_user.is_verified = True
        db.commit()
        db.refresh(db_user)
    else:
        # Create new Google OAuth user
        db_user = User(
            email=req.email,
            name=req.name,
            hashed_password=None,  # No password initially
            oauth_provider="google",
            oauth_id=req.oauth_id,
            avatar_url=req.avatar_url,
            is_verified=True,  # Google emails are pre-verified
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user,
    }


def set_user_password(db: Session, current_user: User, password: str) -> dict:
    """Allows a user (including Google OAuth users) to create or update their password."""
    current_user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}


def request_password_reset(db: Session, email: str) -> dict:
    """Generate password reset token."""
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        # Return generic message to prevent email enumeration
        return {"message": "If this email is registered, a password reset link has been generated."}

    token = secrets.token_urlsafe(32)
    db_user.reset_password_token = token
    db_user.reset_password_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=2)
    db.commit()

    return {
        "message": "If this email is registered, a password reset link has been generated.",
        "reset_token": token,  # In production sent via email
    }


def confirm_password_reset(db: Session, token: str, new_password: str) -> dict:
    """Validate token and reset user password."""
    now = datetime.now(timezone.utc)
    db_user = (
        db.query(User)
        .filter(User.reset_password_token == token)
        .first()
    )
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if db_user.reset_password_token_expires_at:
        expires_at = db_user.reset_password_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise HTTPException(status_code=400, detail="Reset token has expired")

    db_user.hashed_password = get_password_hash(new_password)
    db_user.reset_password_token = None
    db_user.reset_password_token_expires_at = None
    db.commit()

    return {"message": "Password has been reset successfully. You can now log in."}


def verify_email(db: Session, token: str) -> dict:
    """Verify user email with verification token."""
    db_user = db.query(User).filter(User.verification_token == token).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    db_user.is_verified = True
    db_user.verification_token = None
    db_user.verification_token_expires_at = None
    db.commit()

    return {"message": "Email verified successfully"}
