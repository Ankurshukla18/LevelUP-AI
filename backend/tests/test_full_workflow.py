import pytest


@pytest.fixture
def auth_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "workflow_test@example.com", "name": "Workflow User", "password": "securepassword123"}
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "workflow_test@example.com", "password": "securepassword123"}
    )
    return res.json()["access_token"]


def test_complete_scenario_workflow(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Create a goal: "Learn Python"
    goal_payload = {
        "name": "Learn Python",
        "category": "coding",
        "description": "Learn fundamentals and build apps",
        "start_date": "2026-09-29",
        "target_date": "2026-11-24",
        "current_level": "Beginner",
        "target_outcome": "Comfortable with Python",
        "available_hours_per_week": 8.0,
        "priority": "high",
        "motivation": "Career switch"
    }
    create_goal_res = client.post("/api/goals", json=goal_payload, headers=headers)
    assert create_goal_res.status_code == 200
    goal = create_goal_res.json()
    goal_id = goal["id"]
    assert goal["name"] == "Learn Python"

    # 2. Generate AI Roadmap
    roadmap_res = client.post(f"/api/goals/{goal_id}/roadmap/generate", json={}, headers=headers)
    assert roadmap_res.status_code == 200
    roadmap = roadmap_res.json()
    roadmap_id = roadmap["id"]
    assert len(roadmap["weeks"]) > 0
    first_week = roadmap["weeks"][0]
    assert len(first_week["tasks"]) > 0

    # 3. Retrieve Roadmap
    get_roadmap_res = client.get(f"/api/goals/{goal_id}/roadmap", headers=headers)
    assert get_roadmap_res.status_code == 200

    # 4. Submit Weekly Check-in for Week 1
    tasks_checkin = [
        {"task_id": t["id"], "is_completed": i % 2 == 0, "notes": "Done" if i % 2 == 0 else "Pending"}
        for i, t in enumerate(first_week["tasks"])
    ]
    checkin_payload = {
        "week_id": first_week["id"],
        "hours_spent": 7.0,
        "accomplishments": "Completed basic modules and practice",
        "problems_faced": "Loops were tricky",
        "difficulty_level": "moderate",
        "self_rating": 7,
        "notes": "Good first week",
        "tasks": tasks_checkin
    }
    checkin_res = client.post(f"/api/goals/{goal_id}/checkins", json=checkin_payload, headers=headers)
    assert checkin_res.status_code == 200
    checkin = checkin_res.json()
    checkin_id = checkin["id"]
    assert checkin["hours_spent"] == 7.0

    # 5. Progress records should have been automatically calculated
    progress_res = client.get(f"/api/goals/{goal_id}/progress", headers=headers)
    assert progress_res.status_code == 200
    progress_records = progress_res.json()
    assert len(progress_records) >= 1
    latest_progress = progress_records[-1]
    assert latest_progress["time_completion_pct"] > 0

    # 6. AI Weekly Analysis
    analyze_res = client.post(
        f"/api/goals/{goal_id}/analyze",
        json={"checkin_id": checkin_id},
        headers=headers
    )
    assert analyze_res.status_code == 200
    analysis = analyze_res.json()
    analysis_id = analysis["id"]
    assert "summary" in analysis
    assert len(analysis["recommendations"]) > 0

    # 7. Adaptive Roadmap adjustment
    adjust_res = client.post(
        f"/api/goals/{goal_id}/roadmap/adjust",
        json={"analysis_id": analysis_id, "roadmap_id": roadmap_id},
        headers=headers
    )
    assert adjust_res.status_code == 200
    adjustment = adjust_res.json()
    assert adjustment["status"] in ["applied", "pending"]

    # 8. Dashboard analytics
    analytics_res = client.get("/api/dashboard/analytics", headers=headers)
    assert analytics_res.status_code == 200
    analytics = analytics_res.json()
    assert analytics["active_goals_count"] >= 1
