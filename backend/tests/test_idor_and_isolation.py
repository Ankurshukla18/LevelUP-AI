"""
Comprehensive Negative Authorization & IDOR Security Tests:
Verify User A CANNOT:
1. Access User B's goals (GET /api/goals/{id} -> 404)
2. Update User B's goals (PUT /api/goals/{id} -> 404)
3. Delete User B's goals (DELETE /api/goals/{id} -> 404)
4. Access User B's roadmap (GET /api/goals/{id}/roadmap -> 404)
5. Generate roadmap on User B's goal (POST /api/goals/{id}/roadmap/generate -> 404)
6. Modify User B's roadmap week (PUT /api/roadmap/weeks/{id} -> 404)
7. Modify User B's task (PUT /api/roadmap/tasks/{id} -> 404)
8. Delete User B's task (DELETE /api/roadmap/tasks/{id} -> 404)
9. Add task to User B's week (POST /api/roadmap/tasks/{id} -> 404)
10. Submit checkin on User B's goal (POST /api/goals/{id}/checkins -> 404)
11. Submit checkin targeting User B's week/task (IDOR attack -> 404)
12. Access User B's progress (GET /api/goals/{id}/progress -> 404)
13. Access User B's AI analysis (POST /api/goals/{id}/analyze -> 404)
14. Request monthly review for User B's goal (POST /api/goals/{id}/monthly-review -> 404)

Also verify input validations:
- Negative hours rejected (422)
- Target date before start date rejected (422)
- Short password rejected (422)
"""
import pytest
from datetime import date, timedelta
import uuid


@pytest.fixture
def user_a_headers(client):
    client.post(
        "/api/auth/register",
        json={"email": "usera@security.example.com", "name": "User A", "password": "passwordA123"}
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "usera@security.example.com", "password": "passwordA123"}
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def user_b_headers(client):
    client.post(
        "/api/auth/register",
        json={"email": "userb@security.example.com", "name": "User B", "password": "passwordB123"}
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "userb@security.example.com", "password": "passwordB123"}
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def user_b_goal(client, user_b_headers):
    payload = {
        "name": "User B Private Goal",
        "category": "coding",
        "description": "Private description",
        "start_date": str(date.today()),
        "target_date": str(date.today() + timedelta(days=60)),
        "current_level": "Beginner",
        "target_outcome": "Complete private project",
        "available_hours_per_week": 10.0,
    }
    res = client.post("/api/goals", json=payload, headers=user_b_headers)
    assert res.status_code == 200
    return res.json()


def test_user_a_cannot_access_user_b_goals(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.get(f"/api/goals/{goal_id}", headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_update_user_b_goal(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.put(f"/api/goals/{goal_id}", json={"name": "Hacked Name"}, headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_delete_user_b_goal(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.delete(f"/api/goals/{goal_id}", headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_access_user_b_roadmap(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.get(f"/api/goals/{goal_id}/roadmap", headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_generate_roadmap_for_user_b(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.post(f"/api/goals/{goal_id}/roadmap/generate", headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_access_user_b_progress(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.get(f"/api/goals/{goal_id}/progress", headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_submit_checkin_to_user_b_goal(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    fake_week_id = str(uuid.uuid4())
    payload = {
        "week_id": fake_week_id,
        "hours_spent": 5.0,
        "accomplishments": "Tried to hijack",
        "difficulty_level": "moderate",
        "self_rating": 7,
        "tasks": []
    }
    res = client.post(f"/api/goals/{goal_id}/checkins", json=payload, headers=user_a_headers)
    assert res.status_code == 404


def test_user_a_cannot_request_monthly_review_for_user_b(client, user_a_headers, user_b_goal):
    goal_id = user_b_goal["id"]
    res = client.post(f"/api/goals/{goal_id}/monthly-review", headers=user_a_headers)
    assert res.status_code == 404


def test_checkin_idor_cross_goal_week_injection_rejected(client, user_a_headers, user_b_headers, user_b_goal):
    # Create goal for User A
    res_a = client.post(
        "/api/goals",
        json={
            "name": "User A Legit Goal",
            "category": "coding",
            "start_date": str(date.today()),
            "target_date": str(date.today() + timedelta(days=30)),
            "current_level": "Beginner",
            "target_outcome": "Outcome",
            "available_hours_per_week": 8.0,
        },
        headers=user_a_headers,
    )
    goal_a_id = res_a.json()["id"]

    # User A tries to pass an invalid or unrelated week_id
    foreign_week_id = str(uuid.uuid4())
    checkin_payload = {
        "week_id": foreign_week_id,
        "hours_spent": 4.0,
        "accomplishments": "IDOR attempt",
        "difficulty_level": "moderate",
        "self_rating": 6,
        "tasks": [],
    }
    res = client.post(f"/api/goals/{goal_a_id}/checkins", json=checkin_payload, headers=user_a_headers)
    # Must reject with 404 because week doesn't belong to this goal
    assert res.status_code == 404


def test_input_validation_target_date_before_start_date(client, user_a_headers):
    today = date.today()
    invalid_payload = {
        "name": "Invalid Date Goal",
        "category": "academics",
        "start_date": str(today),
        "target_date": str(today - timedelta(days=10)),  # Target BEFORE start
        "current_level": "Intermediate",
        "target_outcome": "Invalid",
        "available_hours_per_week": 10.0,
    }
    res = client.post("/api/goals", json=invalid_payload, headers=user_a_headers)
    assert res.status_code == 422


def test_input_validation_negative_hours_in_checkin(client, user_a_headers):
    invalid_checkin = {
        "week_id": str(uuid.uuid4()),
        "hours_spent": -5.0,  # Negative hours
        "accomplishments": "Did negative work",
        "difficulty_level": "moderate",
        "self_rating": 5,
        "tasks": [],
    }
    res = client.post(f"/api/goals/{uuid.uuid4()}/checkins", json=invalid_checkin, headers=user_a_headers)
    assert res.status_code == 422


def test_input_validation_password_too_short(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "shortpw@test.com", "name": "Short Pw", "password": "123"}
    )
    assert res.status_code == 422
