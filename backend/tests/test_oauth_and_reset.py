import json
import pytest
from unittest.mock import MagicMock, patch
from app.config import settings


@pytest.fixture(autouse=True)
def setup_oauth_test_settings(monkeypatch):
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-google-client-id")
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", "test-google-client-secret")
    monkeypatch.setattr(settings, "GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google")
    monkeypatch.setattr(settings, "FRONTEND_URL", "http://localhost:3000")


class MockGoogleResponse:
    def __init__(self, status_code: int, json_data: dict, text: str = ""):
        self.status_code = status_code
        self._json = json_data
        self.text = text or json.dumps(json_data)

    def json(self):
        return self._json


def _build_google_mock_client(userinfo: dict, valid_code: str = "valid-google-code"):
    """Creates a mock httpx.Client that simulates Google OAuth token exchange and userinfo."""
    mock_client = MagicMock()
    mock_client.token_post_data = []

    def mock_post(url, **kwargs):
        data = kwargs.get("data", {})
        if "oauth2.googleapis.com/token" in url:
            mock_client.token_post_data.append(data)
            if data.get("code") == valid_code:
                return MockGoogleResponse(200, {"access_token": "google-valid-access-token"})
            return MockGoogleResponse(400, {"error": "invalid_grant"}, text="Invalid authorization code")
        return MockGoogleResponse(404, {})

    def mock_get(url, **kwargs):
        headers = kwargs.get("headers", {})
        if "googleapis.com/oauth2/v3/userinfo" in url:
            if "Bearer google-valid-access-token" in headers.get("Authorization", ""):
                return MockGoogleResponse(200, userinfo)
            return MockGoogleResponse(401, {"error": "unauthorized"})
        return MockGoogleResponse(404, {})

    mock_client.post.side_effect = mock_post
    mock_client.get.side_effect = mock_get
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    return mock_client


# ===========================================================================
# 1. Complete Valid Google OAuth Flow (Code Exchange -> User -> Password Setup)
# ===========================================================================

def test_google_oauth_complete_flow_with_mandatory_password(client):
    """
    Verifies the complete, legitimate Google OAuth 2.0 flow:
    1. Valid auth code exchanged with Google -> Account created in PostgreSQL
    2. requires_password_setup is True
    3. User sets password via /api/auth/create-password
    4. Subsequent Google login has requires_password_setup == False
    5. User can also log in via email + password with the EXACT SAME user_id
    6. No duplicate account is created
    """
    google_email = "new_google_student@gmail.com"
    userinfo = {
        "email": google_email,
        "name": "Google Student",
        "sub": "google-sub-987654321",
        "picture": "https://lh3.googleusercontent.com/photo.jpg",
    }
    mock_httpx = _build_google_mock_client(userinfo, valid_code="valid-google-code")

    with patch("httpx.Client", return_value=mock_httpx):
        # Step 1: User authenticates with valid Google code
        cb_res = client.post(
            "/api/auth/google/callback",
            json={"code": "valid-google-code"}
        )
        assert cb_res.status_code == 200
        auth_data = cb_res.json()
        assert auth_data["requires_password_setup"] is True, "New Google user must require password setup!"
        assert auth_data["user"]["email"] == google_email
        assert auth_data["user"]["oauth_provider"] == "google"
        user_id_1 = auth_data["user"]["id"]
        token = auth_data["access_token"]
        assert token is not None

        # Step 2: User sets their mandatory password via /api/auth/create-password
        create_pw_res = client.post(
            "/api/auth/create-password",
            json={"password": "MySecretPassword123!", "confirm_password": "MySecretPassword123!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_pw_res.status_code == 200
        pw_data = create_pw_res.json()
        assert pw_data["requires_password_setup"] is False
        assert pw_data["user"]["has_password"] is True
        assert pw_data["user"]["id"] == user_id_1

        # Step 3: Subsequent Google login bypasses password creation (direct login)
        subsequent_google_res = client.post(
            "/api/auth/google/callback",
            json={"code": "valid-google-code"}
        )
        assert subsequent_google_res.status_code == 200
        sub_data = subsequent_google_res.json()
        assert sub_data["requires_password_setup"] is False, "Existing Google user with password should not require setup!"
        assert sub_data["user"]["id"] == user_id_1

        # Step 4: Same user logs in with traditional email + password
        email_login_res = client.post(
            "/api/auth/login",
            json={"email": google_email, "password": "MySecretPassword123!"}
        )
        assert email_login_res.status_code == 200
        login_data = email_login_res.json()
        assert login_data["user"]["id"] == user_id_1, "Email login must resolve to the exact same user_id!"
        assert login_data["requires_password_setup"] is False


# ===========================================================================
# 2. Account Linking Flow
# ===========================================================================

def test_duplicate_email_account_linking(client):
    """
    Verifies that if an email user already exists, signing in with Google
    links the account to the existing user_id without creating duplicate accounts.
    """
    existing_email = "pre_existing_student@example.com"

    # 1. Register with email + password first
    reg_res = client.post(
        "/api/auth/register",
        json={"name": "Pre Existing", "email": existing_email, "password": "InitialPassword123!"}
    )
    assert reg_res.status_code == 200
    original_user_id = reg_res.json()["id"]

    # 2. User clicks 'Continue with Google' with the same email
    userinfo = {
        "email": existing_email,
        "name": "Pre Existing",
        "sub": "google-linked-id-555",
        "picture": "https://lh3.googleusercontent.com/photo.jpg",
    }
    mock_httpx = _build_google_mock_client(userinfo, valid_code="linking-code")

    with patch("httpx.Client", return_value=mock_httpx):
        google_link_res = client.post(
            "/api/auth/google/callback",
            json={"code": "linking-code"}
        )
        assert google_link_res.status_code == 200
        linked_data = google_link_res.json()
        assert linked_data["user"]["id"] == original_user_id, "Must link to the existing account ID!"
        assert linked_data["requires_password_setup"] is False


# ===========================================================================
# 3. Password Reset Flow Endpoints Removed
# ===========================================================================

def test_password_reset_endpoints_are_removed(client):
    """Verifies that the removed forgot-password and reset-password routes return 404."""
    forgot_res = client.post("/api/auth/forgot-password", json={"email": "anyone@example.com"})
    assert forgot_res.status_code == 404

    reset_res = client.post("/api/auth/reset-password", json={"token": "any-token", "new_password": "newpassword123"})
    assert reset_res.status_code == 404


# ===========================================================================
# 4. REGRESSION TESTS: AUTHENTICATION BYPASS PREVENTION
# ===========================================================================

def test_direct_google_endpoint_cannot_authenticate_with_arbitrary_email(client):
    """
    CRITICAL REGRESSION TEST:
    Verifies that POST /api/auth/google cannot authenticate a user merely from
    arbitrary email, name, or oauth_id. The route has been disabled/removed.
    """
    res = client.post(
        "/api/auth/google",
        json={
            "email": "victim_target@university.edu",
            "name": "Target Student",
            "oauth_id": "forged_oauth_12345"
        }
    )
    # The insecure direct route must be rejected (404 Not Found or 405 Method Not Allowed)
    assert res.status_code in [404, 405]
    assert "access_token" not in res.text


def test_callback_missing_code_rejected(client):
    """
    REGRESSION TEST:
    Verifies that calling /api/auth/google/callback without an authorization
    code returns 400 Bad Request and does not issue a JWT.
    """
    res = client.post("/api/auth/google/callback", json={})
    assert res.status_code == 400
    assert "Authorization code is required" in res.json().get("detail", "")
    assert "access_token" not in res.text


def test_callback_fake_mock_email_cannot_produce_jwt(client):
    """
    CRITICAL REGRESSION TEST:
    Verifies that supplying a mock_email to /api/auth/google/callback cannot bypass
    Google authorization or produce a JWT when mock mode is not enabled.
    """
    res = client.post(
        "/api/auth/google/callback",
        json={
            "mock_email": "victim_account@gmail.com",
            "mock_name": "Victim",
            "mock_oauth_id": "fake_123"
        }
    )
    assert res.status_code == 400
    assert "Authorization code is required" in res.json().get("detail", "")
    assert "access_token" not in res.text


def test_callback_fake_code_rejected(client):
    """
    REGRESSION TEST:
    Verifies that submitting an invalid or forged authorization code is rejected
    when Google token exchange fails.
    """
    userinfo = {"email": "test@gmail.com"}
    mock_httpx = _build_google_mock_client(userinfo, valid_code="real-code")

    with patch("httpx.Client", return_value=mock_httpx):
        res = client.post(
            "/api/auth/google/callback",
            json={"code": "tampered-fake-code"}
        )
        assert res.status_code == 400
        assert "Failed to exchange authorization code" in res.json().get("detail", "")
        assert "access_token" not in res.text


def test_mock_mode_strictly_disabled_in_production(client):
    """
    SECURITY TEST:
    Verifies that even if ENABLE_OAUTH_MOCK were accidentally set to True,
    when ENVIRONMENT=production, mock authentication is strictly rejected.
    """
    with patch.object(settings, "ENABLE_OAUTH_MOCK", True), \
         patch.object(settings, "ENVIRONMENT", "production"):
        res = client.post(
            "/api/auth/google/callback",
            json={"mock_email": "hack_attempt@target.com"}
        )
        assert res.status_code == 400
        assert "Authorization code is required" in res.json().get("detail", "")
        assert "access_token" not in res.text


def test_existing_email_password_login_still_works(client):
    """
    REGRESSION TEST:
    Confirms standard email + password registration and login remains completely functional.
    """
    email = "standard_student@university.edu"
    password = "CorrectHorseBattery99!"

    # Register
    reg_res = client.post(
        "/api/auth/register",
        json={"email": email, "name": "Standard Student", "password": password}
    )
    assert reg_res.status_code == 200

    # Login
    login_res = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email


def test_google_oauth_redirect_uri_environment_aware(client):
    """
    Verifies that:
    1. GET /api/auth/google/url accepts custom redirect_uri when origin matches FRONTEND_URL or CORS
    2. POST /api/auth/google/callback forwards the custom redirect_uri to Google token endpoint
    """
    custom_redirect = "http://localhost:3000/auth/callback/google"
    url_res = client.get(f"/api/auth/google/url?redirect_uri={custom_redirect}")
    assert url_res.status_code == 200
    assert custom_redirect in url_res.json()["url"]

    # Test with custom production origin configured in FRONTEND_URL
    with patch.object(settings, "FRONTEND_URL", "https://levelup-ai.vercel.app"):
        prod_redirect = "https://levelup-ai.vercel.app/auth/callback/google"
        url_res_prod = client.get(f"/api/auth/google/url?redirect_uri={prod_redirect}")
        assert url_res_prod.status_code == 200
        assert prod_redirect in url_res_prod.json()["url"]

        # Token exchange uses prod_redirect
        userinfo = {"email": "prod_user@example.com", "name": "Prod User", "sub": "sub123"}
        mock_httpx = _build_google_mock_client(userinfo, valid_code="prod-code")
        with patch("httpx.Client", return_value=mock_httpx):
            cb_res = client.post(
                "/api/auth/google/callback",
                json={"code": "prod-code", "redirect_uri": prod_redirect}
            )
            assert cb_res.status_code == 200
            assert len(mock_httpx.token_post_data) > 0
            assert mock_httpx.token_post_data[0]["redirect_uri"] == prod_redirect


def test_google_oauth_rejects_untrusted_redirect_uri_origin(client):
    """
    Verifies that an untrusted phishing/malicious origin falls back to the safe default redirect URI.
    """
    malicious_uri = "https://evil-phishing-site.com/auth/callback/google"
    url_res = client.get(f"/api/auth/google/url?redirect_uri={malicious_uri}")
    assert url_res.status_code == 200
    # Must NOT use the malicious domain, falls back to settings.GOOGLE_REDIRECT_URI
    assert "evil-phishing-site.com" not in url_res.json()["url"]

