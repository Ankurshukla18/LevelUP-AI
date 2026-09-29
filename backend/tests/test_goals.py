import pytest

@pytest.fixture
def token(client):
    client.post("/api/auth/register", json={"email": "goal_test@example.com", "name": "Test", "password": "password123"})
    response = client.post("/api/auth/login", json={"email": "goal_test@example.com", "password": "password123"})
    return response.json()["access_token"]

def test_create_goal(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    goal_data = {
        "name": "Test Goal",
        "category": "coding",
        "start_date": "2023-01-01",
        "target_date": "2023-12-31",
        "current_level": "beginner",
        "target_outcome": "expert",
        "available_hours_per_week": 10.0
    }
    response = client.post("/api/goals", json=goal_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Goal"

def test_get_goals(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/goals", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
