"""
Regression tests for JWT SECRET_KEY Security & Production Readiness (Audit Finding #2):
1. production + missing SECRET_KEY -> configuration/startup failure
2. production + default placeholder -> failure
3. production + short secret (< 32 chars) -> failure
4. production + valid strong secret (>= 32 chars) -> success
5. development + valid local secret -> success
6. JWT created with the configured secret can still be verified
7. JWT signed with a different secret is rejected (both at crypto layer and HTTP API)
"""
import pytest
import secrets
from pydantic import ValidationError
from jose import jwt, JWTError

from app.config import Settings, settings
from app.utils.security import create_access_token


# ===========================================================================
# 1. Production + Missing SECRET_KEY -> Failure
# ===========================================================================

def test_production_missing_secret_key_fails():
    """Application startup/config must fail if SECRET_KEY is missing/empty in production."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(ENVIRONMENT="production", SECRET_KEY="")
    errors = str(exc_info.value)
    assert "SECRET_KEY is required and cannot be empty in production" in errors


# ===========================================================================
# 2. Production + Default Insecure Placeholder -> Failure
# ===========================================================================

@pytest.mark.parametrize("placeholder", [
    "your-super-secret-key-change-in-production",
    "your_super_secret_key_minimum_32_characters_here",
    "CHANGE_ME_TO_A_RANDOM_32_BYTE_SECRET",
    "dev-insecure-secret-key-for-local-development-only-32chars",
    "changeme",
    "secret",
])
def test_production_default_placeholder_fails(placeholder):
    """Application startup/config must fail if SECRET_KEY matches known placeholders in production."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(ENVIRONMENT="production", SECRET_KEY=placeholder)
    errors = str(exc_info.value)
    assert "insecure placeholder or default" in errors.lower()
    # Confirm secret value is not printed
    assert placeholder not in errors or len(placeholder) < 15


# ===========================================================================
# 3. Production + Short Secret (< 32 chars / 256 bits) -> Failure
# ===========================================================================

@pytest.mark.parametrize("short_secret", [
    "short_key",
    "1234567890123456789012345678901",  # 31 chars
    "a" * 16,
])
def test_production_short_secret_fails(short_secret):
    """Production requires at least 32 characters (256 bits) of entropy."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(ENVIRONMENT="production", SECRET_KEY=short_secret)
    errors = str(exc_info.value)
    assert "minimum entropy requirements" in errors.lower()


# ===========================================================================
# 4. Production + Valid Strong Secret (>= 32 chars) -> Success
# ===========================================================================

def test_production_valid_strong_secret_succeeds():
    """Production succeeds when provided with a strong 32+ character high-entropy key."""
    strong_secret = secrets.token_hex(32)  # 64 chars
    config = Settings(ENVIRONMENT="production", SECRET_KEY=strong_secret)
    assert config.ENVIRONMENT == "production"
    assert config.SECRET_KEY == strong_secret
    assert len(config.SECRET_KEY) >= 32


# ===========================================================================
# 5. Development + Valid Local Secret -> Success
# ===========================================================================

def test_development_valid_local_secret_succeeds():
    """Development succeeds with configured local secret."""
    dev_secret = "my-local-dev-secret-key-12345"
    config = Settings(ENVIRONMENT="development", SECRET_KEY=dev_secret)
    assert config.ENVIRONMENT == "development"
    assert config.SECRET_KEY == dev_secret


# ===========================================================================
# 6. JWT Created with Configured Secret Can Be Verified
# ===========================================================================

def test_jwt_created_with_configured_secret_can_be_verified():
    """JWT created using application utility is verified against configured SECRET_KEY."""
    payload = {"sub": "verified_user@university.edu"}
    token = create_access_token(payload)

    # Verify decoding with the configured settings.SECRET_KEY
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "verified_user@university.edu"
    assert "exp" in decoded


# ===========================================================================
# 7. JWT Signed with Different Secret Is Rejected
# ===========================================================================

def test_jwt_signed_with_different_secret_is_rejected(client):
    """
    Cryptographic verification must reject tokens signed with a different key.
    Protected API endpoints must reject them with HTTP 401 Unauthorized.
    """
    foreign_secret = secrets.token_hex(32)
    forged_token = jwt.encode(
        {"sub": "victim_target@university.edu"},
        foreign_secret,
        algorithm=settings.ALGORITHM,
    )

    # 1. Direct crypto layer verification fails
    with pytest.raises(JWTError):
        jwt.decode(forged_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    # 2. HTTP API layer rejects forged token on protected endpoint (/api/auth/me)
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json().get("detail", "")
