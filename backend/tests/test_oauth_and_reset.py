def test_google_oauth_registration_and_login(client):
    google_payload = {
        "email": "google_student@example.com",
        "name": "Google User",
        "oauth_id": "google-sub-12345678",
        "avatar_url": "https://lh3.googleusercontent.com/a/sample-photo"
    }
    # 1. First time Google login creates verified account
    res = client.post("/api/auth/google", json=google_payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "google_student@example.com"
    assert data["user"]["is_verified"] is True
    assert data["user"]["oauth_provider"] == "google"

    # 2. Subsequent Google login re-authenticates and returns valid token
    res2 = client.post("/api/auth/google", json=google_payload)
    assert res2.status_code == 200
    assert "access_token" in res2.json()

    # 3. Google user creates a password
    token = data["access_token"]
    set_pw_res = client.post(
        "/api/auth/set-password",
        json={"password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert set_pw_res.status_code == 200
    assert "message" in set_pw_res.json()

    # 4. User can now also log in using email and the newly created password!
    email_login_res = client.post(
        "/api/auth/login",
        json={"email": "google_student@example.com", "password": "newpassword123"}
    )
    assert email_login_res.status_code == 200
    assert "access_token" in email_login_res.json()


def test_password_reset_flow(client):
    # Register user
    client.post(
        "/api/auth/register",
        json={"email": "reset_user@example.com", "name": "Reset User", "password": "oldpassword123"}
    )

    # Request password reset
    forgot_res = client.post(
        "/api/auth/forgot-password",
        json={"email": "reset_user@example.com"}
    )
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json().get("reset_token")
    assert reset_token is not None

    # Reset password with token
    reset_res = client.post(
        "/api/auth/reset-password",
        json={"token": reset_token, "new_password": "supernewpassword456"}
    )
    assert reset_res.status_code == 200

    # Old password fails
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "reset_user@example.com", "password": "oldpassword123"}
    )
    assert bad_login.status_code == 401

    # New password succeeds
    good_login = client.post(
        "/api/auth/login",
        json={"email": "reset_user@example.com", "password": "supernewpassword456"}
    )
    assert good_login.status_code == 200
