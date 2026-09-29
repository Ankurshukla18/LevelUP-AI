import secrets
import logging
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import httpx

from ..config import settings
from ..schemas.user import (
    UserCreate,
    UserLogin,
    GoogleAuthRequest,
    GoogleCallbackRequest,
    CreateFirstPasswordRequest,
)
from ..models.user import User
from ..utils.security import get_password_hash, verify_password, create_access_token

logger = logging.getLogger(__name__)


def register_user(db: Session, user: UserCreate) -> User:
    """Register a new user with email and password."""
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
    """
    Authenticate a user via email and password.
    Works for both traditional users and Google OAuth users who have created a password.
    """
    email = user.get_email()
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # If account was created with Google OAuth and no password has been configured yet
    if not db_user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was registered with Google Sign-In and has not set a password yet. Please click 'Continue with Google'.",
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
        "requires_password_setup": False,
        "user": db_user,
    }


def resolve_google_redirect_uri(requested_uri: Optional[str] = None) -> str:
    """
    Resolves and validates the Google OAuth redirect URI.
    If requested_uri is provided by the frontend (e.g. from window.location.origin
    or environment variables), verifies that its origin matches allowed origins
    (CORS origins, FRONTEND_URL, or localhost in development).
    Falls back to settings.GOOGLE_REDIRECT_URI.
    """
    default_uri = (
        settings.GOOGLE_REDIRECT_URI
        or f"{(settings.FRONTEND_URL or 'http://localhost:3000').rstrip('/')}/auth/callback/google"
    )
    if not requested_uri or not requested_uri.strip():
        return default_uri

    clean_uri = requested_uri.strip()
    parsed = urlparse(clean_uri)
    if not parsed.scheme or not parsed.netloc:
        return default_uri

    origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")

    # Permitted origins: CORS origins + FRONTEND_URL
    allowed = {o.rstrip("/") for o in settings.cors_origins}
    if settings.FRONTEND_URL:
        allowed.add(settings.FRONTEND_URL.rstrip("/"))

    is_dev = getattr(settings, "ENVIRONMENT", "").lower() != "production"
    is_localhost = parsed.netloc.startswith("localhost") or parsed.netloc.startswith("127.0.0.1")

    if origin in allowed or (is_dev and is_localhost):
        return clean_uri

    logger.warning(
        f"Requested redirect_uri origin '{origin}' is not in allowed origins. Falling back to default: {default_uri}"
    )
    return default_uri


def get_google_authorization_url(requested_uri: Optional[str] = None) -> dict:
    """
    Generate Google OAuth 2.0 authorization URL.
    Secrets are kept strictly in backend settings.
    """
    redirect_uri = resolve_google_redirect_uri(requested_uri)

    if settings.GOOGLE_CLIENT_ID:
        # Standard Google OAuth 2.0 / OpenID Connect URL
        base = "https://accounts.google.com/o/oauth2/v2/auth"
        params = (
            f"?client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
            f"&access_type=offline"
            f"&prompt=select_account"
        )
        return {
            "url": base + params,
            "auth_url": base + params,
            "redirect_uri": redirect_uri,
            "mock": False,
            "is_mock": False,
        }
    else:
        # Development simulation only when explicitly enabled AND never in production
        is_mock_allowed = (
            getattr(settings, "ENABLE_OAUTH_MOCK", False) is True
            and getattr(settings, "ENVIRONMENT", "").lower() != "production"
        )
        if is_mock_allowed:
            mock_callback_url = f"{redirect_uri}?mock=true"
            return {
                "url": mock_callback_url,
                "auth_url": mock_callback_url,
                "redirect_uri": redirect_uri,
                "mock": True,
                "is_mock": True,
                "note": "Google OAuth credentials not configured; mock simulation mode enabled for development."
            }
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured on this server.",
        )


def process_google_callback(db: Session, req: GoogleCallbackRequest) -> dict:
    """
    Handles Google OAuth callback:
    1. Strictly validates Google authorization code with official Google OAuth endpoints.
    2. Finds existing user by email or creates a new user.
    3. If new or user has no password -> requires_password_setup = True.
    4. If user already created password -> requires_password_setup = False.
    5. Returns JWT access token and user profile.
    """
    email = None
    name = None
    oauth_id = None
    avatar_url = None

    # Check whether development mock mode is explicitly permitted (never in production)
    is_mock_allowed = (
        getattr(settings, "ENABLE_OAUTH_MOCK", False) is True
        and getattr(settings, "ENVIRONMENT", "").lower() != "production"
    )

    # Handle real Google OAuth code exchange
    if req.code:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            logger.error("Google OAuth client ID or client secret is not configured on the server.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not properly configured on the server.",
            )
        resolved_redirect_uri = resolve_google_redirect_uri(req.redirect_uri)
        try:
            with httpx.Client(timeout=10.0) as client:
                token_res = client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": req.code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": resolved_redirect_uri,
                        "grant_type": "authorization_code",
                    },
                )
                if token_res.status_code != 200:
                    logger.error(f"Google token exchange failed: {token_res.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to exchange authorization code with Google.",
                    )

                tokens = token_res.json()
                access_token = tokens.get("access_token")
                if not access_token:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Google OAuth response missing access token.",
                    )

                # Fetch verified user profile directly from Google
                userinfo_res = client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if userinfo_res.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to fetch user profile from Google.",
                    )

                userinfo = userinfo_res.json()
                email = userinfo.get("email")
                name = userinfo.get("name") or (email.split("@")[0] if email else "Google User")
                oauth_id = userinfo.get("sub")
                avatar_url = userinfo.get("picture")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error communicating with Google OAuth: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OAuth communication error: {str(e)}",
            )
    elif is_mock_allowed and req.mock_email:
        # Development-only sandbox simulation, strictly disabled in production
        logger.warning(f"Using development mock Google login for: {req.mock_email}")
        email = req.mock_email
        name = req.mock_name or "Demo User"
        oauth_id = req.mock_oauth_id or f"google-sub-{secrets.token_hex(8)}"
        avatar_url = req.mock_avatar or "https://api.dicebear.com/7.x/avataaars/svg?seed=GoogleUser"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code is required for Google authentication.",
        )

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not return a valid email address.",
        )

    # Check if user already exists in database
    db_user = db.query(User).filter(User.email == email).first()

    if db_user:
        # Existing user: Link Google account if not linked
        if not db_user.oauth_provider:
            db_user.oauth_provider = "google"
            db_user.oauth_id = oauth_id
        if avatar_url and not db_user.avatar_url:
            db_user.avatar_url = avatar_url
        db_user.is_verified = True
        db.commit()
        db.refresh(db_user)

        # Check if user already has a password configured
        has_password = bool(db_user.hashed_password)
        requires_password_setup = not has_password
    else:
        # New Google user: Create account without password
        db_user = User(
            email=email,
            name=name,
            hashed_password=None,
            oauth_provider="google",
            oauth_id=oauth_id,
            avatar_url=avatar_url,
            is_verified=True,  # Google verified
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # New Google account must configure a password
        requires_password_setup = True

    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_password_setup": requires_password_setup,
        "user": db_user,
    }


def create_first_password(db: Session, current_user: User, req: CreateFirstPasswordRequest) -> dict:
    """
    Mandatory password creation for newly created Google users.
    Validates password, hashes with bcrypt, updates user, and unlocks dashboard access.
    """
    if req.confirm_password and req.password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )

    if len(req.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long.",
        )

    current_user.hashed_password = get_password_hash(req.password)
    db.commit()
    db.refresh(current_user)

    # Issue fresh token
    access_token = create_access_token(data={"sub": current_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_password_setup": False,
        "message": "Password created successfully! You can now log in with either Google or email + password.",
        "user": current_user,
    }


def set_user_password(db: Session, current_user: User, password: str) -> dict:
    """Allows an authenticated user to update their password."""
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    current_user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}


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
