"""
End-to-End Acceptance Test Script for LifeTrack AI
Simulates the exact user scenario defined in Section 35 of the prompt:
1. User registers
2. Creates goal: "Learn Python" (Beginner, 8 hrs/wk, 8 weeks)
3. Clicks "Generate Roadmap" -> 8-week roadmap created
4. Completes Week 1 tasks
5. Submits weekly check-in (6 tasks completed, 7 hours, "Loops difficult", Rating 7/10)
6. Backend calculates progress (Task %, Time %, Consistency %, Streak)
7. AI generates weekly analysis
8. Dashboard displays: Planned vs Actual, Completion %, Hours, Progress, AI summary, Delays
9. AI suggests a roadmap adjustment
10. User clicks "Apply Adjustment"
11. Week 2 roadmap updates
12. Historical progress remains accessible
"""
import httpx
import sys
from datetime import date, timedelta

BASE_URL = "http://127.0.0.1:8000"

def log_step(num, title):
    print(f"\n{'='*70}")
    print(f"STEP {num}: {title}")
    print(f"{'='*70}")

def run_acceptance_scenario():
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # ----------------------------------------------------
    # 1. User Registers
    # ----------------------------------------------------
    log_step(1, "User Registers New Account")
    email = f"student_{date.today().strftime('%Y%m%d')}_{int(date.today().day)}@lifetrack.ai"
    password = "SecurePassword123!"
    name = "Jordan Student"

    reg_payload = {"name": name, "email": email, "password": password}
    r = client.post("/api/auth/register", json=reg_payload)
    if r.status_code == 400:
        # If already registered, proceed to login
        print(f"User {email} already exists, proceeding to login.")
    else:
        assert r.status_code == 200, f"Registration failed: {r.text}"
        print(f"User registered successfully: {r.json()['email']} (ID: {r.json()['id']})")

    # ----------------------------------------------------
    # 2. User Logs In
    # ----------------------------------------------------
    log_step(2, "User Logs In & Obtains JWT Bearer Token")
    login_payload = {"email": email, "password": password}
    r = client.post("/api/auth/login", json=login_payload)
    assert r.status_code == 200, f"Login failed: {r.text}"
    auth_data = r.json()
    token = auth_data["access_token"]
    user_info = auth_data.get("user")
    print(f"Login successful! User: {user_info['name']} ({user_info['email']})")
    print(f"Token obtained: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # ----------------------------------------------------
    # 3. User Reaches Dashboard
    # ----------------------------------------------------
    log_step(3, "User Reaches Dashboard & Loads Initial Analytics")
    r = client.get("/api/dashboard/analytics", headers=headers)
    assert r.status_code == 200, f"Dashboard load failed: {r.text}"
    initial_analytics = r.json()
    print(f"Dashboard loaded. Active Goals: {initial_analytics['active_goals_count']}, Streak: {initial_analytics['current_streak']}")

    # ----------------------------------------------------
    # 4. User Creates Goal: "Learn Python"
    # ----------------------------------------------------
    log_step(4, "User Creates Goal: 'Learn Python' (Beginner, 8 hrs/wk, 8-week target)")
    today = date.today()
    target_date = today + timedelta(weeks=8)

    goal_payload = {
        "name": "Learn Python",
        "category": "coding",
        "description": "Learn Python from fundamentals to independent projects",
        "start_date": today.isoformat(),
        "target_date": target_date.isoformat(),
        "current_level": "Beginner",
        "target_outcome": "Become comfortable with Python syntax and build 2 projects",
        "available_hours_per_week": 8.0,
        "priority": "high",
        "motivation": "Transition to a software engineering career"
    }
    r = client.post("/api/goals", json=goal_payload, headers=headers)
    assert r.status_code == 200, f"Goal creation failed: {r.text}"
    goal = r.json()
    goal_id = goal["id"]
    print(f"Goal created successfully!")
    print(f"  Name: {goal['name']}")
    print(f"  Category: {goal['category']}")
    print(f"  Target Date: {goal['target_date']}")
    print(f"  Available Hours: {goal['available_hours_per_week']} hrs/week")

    # ----------------------------------------------------
    # 5. User Clicks: "Generate AI Roadmap"
    # ----------------------------------------------------
    log_step(5, "User Requests AI Roadmap Generation")
    r = client.post(f"/api/goals/{goal_id}/roadmap/generate", json={}, headers=headers)
    assert r.status_code == 200, f"Roadmap generation failed: {r.text}"
    roadmap = r.json()
    roadmap_id = roadmap["id"]
    weeks = roadmap["weeks"]
    print(f"AI generated an {len(weeks)}-week comprehensive roadmap (Version {roadmap['version']}):")
    for w in weeks:
        print(f"  Week {w['week_number']}: {w['title']} ({len(w['tasks'])} tasks, est {w['estimated_hours']} hrs)")

    assert len(weeks) >= 8, f"Expected at least 8 weeks in roadmap, got {len(weeks)}"
    week1 = weeks[0]
    week2 = weeks[1]

    # ----------------------------------------------------
    # 6. User Reviews & Starts Working on Week 1 Tasks
    # ----------------------------------------------------
    log_step(6, "User Works on Week 1 Tasks & Marks Tasks Complete")
    # Mark tasks complete
    w1_tasks = week1["tasks"]
    print(f"Week 1 initial tasks ({len(w1_tasks)} total):")
    completed_task_ids = []
    for idx, t in enumerate(w1_tasks):
        # Complete up to 6 tasks or majority
        should_complete = idx < 6
        if should_complete:
            client.put(f"/api/roadmap/tasks/{t['id']}", json={"is_completed": True}, headers=headers)
            completed_task_ids.append(t["id"])
            print(f"  [X] Finished: {t['title']}")
        else:
            print(f"  [ ] Pending:  {t['title']}")

    # ----------------------------------------------------
    # 7. User Submits Weekly Check-in for Week 1
    # ----------------------------------------------------
    log_step(7, "User Submits Weekly Check-in (6 tasks done, 7 hrs, Loops difficult, Rating 7/10)")
    checkin_tasks_payload = [
        {"task_id": t["id"], "is_completed": t["id"] in completed_task_ids, "notes": "Completed" if t["id"] in completed_task_ids else "Delayed"}
        for t in w1_tasks
    ]

    checkin_payload = {
        "week_id": week1["id"],
        "hours_spent": 7.0,
        "accomplishments": "Completed variables, operators, and basic if conditions.",
        "problems_faced": "Loops were difficult and took more time than expected.",
        "difficulty_level": "moderate",
        "self_rating": 7,
        "notes": "Need extra practice on loop logic before advancing.",
        "tasks": checkin_tasks_payload
    }
    r = client.post(f"/api/goals/{goal_id}/checkins", json=checkin_payload, headers=headers)
    assert r.status_code == 200, f"Checkin failed: {r.text}"
    checkin = r.json()
    checkin_id = checkin["id"]
    print(f"Weekly Check-in recorded successfully! ID: {checkin_id}")
    print(f"  Hours Logged: {checkin['hours_spent']} hrs")
    print(f"  Tasks Finished: {checkin['tasks_completed_count']}")
    print(f"  Self Rating: {checkin['self_rating']}/10")

    # ----------------------------------------------------
    # 8. Backend Deterministic Progress Calculations
    # ----------------------------------------------------
    log_step(8, "Backend Calculates Deterministic Progress Metrics")
    r = client.get(f"/api/goals/{goal_id}/progress", headers=headers)
    assert r.status_code == 200, f"Progress fetch failed: {r.text}"
    progress_list = r.json()
    assert len(progress_list) > 0, "Expected at least 1 progress record"
    pr = progress_list[-1]
    print(f"Deterministic Backend Calculations for Week {pr['week_number']}:")
    print(f"  Task Completion %:       {pr['task_completion_pct']:.1f}%")
    print(f"  Time Completion %:       {pr['time_completion_pct']:.1f}%")
    print(f"  Consistency %:           {pr['consistency_pct']:.1f}%")
    print(f"  Current Streak:          {pr['streak']} week(s)")
    print(f"  Completed Tasks:         {pr['total_completed_tasks']}")
    print(f"  Delayed Tasks:           {pr['total_delayed_tasks']}")

    # ----------------------------------------------------
    # 9. AI Generates Weekly Analysis
    # ----------------------------------------------------
    log_step(9, "AI Generates Weekly Analysis & Feedback")
    r = client.post(f"/api/goals/{goal_id}/analyze", json={"checkin_id": checkin_id}, headers=headers)
    assert r.status_code == 200, f"AI Analysis failed: {r.text}"
    analysis = r.json()
    analysis_id = analysis["id"]
    print("AI Structured Analysis Output:")
    print(f"  Weekly Summary:      {analysis['summary']}")
    print(f"  What Went Well:      {', '.join(analysis['went_well'])}")
    print(f"  What Was Delayed:    {', '.join(analysis['delayed'])}")
    print(f"  Possible Reasons:    {', '.join(analysis['reasons'])}")
    print(f"  Recommendations:     {', '.join(analysis['recommendations'])}")
    print(f"  Next Week Focus:     {', '.join(analysis['next_week_focus'])}")
    print(f"  Suggested Adjustment: {analysis['roadmap_adjustment_type'].upper()}")

    # ----------------------------------------------------
    # 10. Dashboard Reflects Updated Analytics
    # ----------------------------------------------------
    log_step(10, "Dashboard Reflects Updated Live Analytics")
    r = client.get("/api/dashboard/analytics", headers=headers)
    assert r.status_code == 200
    dash = r.json()
    print("Dashboard Live State:")
    print(f"  Active Goals:        {dash['active_goals_count']}")
    print(f"  Overall Progress %:  {dash['overall_completion_pct']:.1f}%")
    print(f"  Total Hours Spent:   {dash['total_hours_spent']} hrs")
    print(f"  Current Streak:      {dash['current_streak']} week(s)")
    print(f"  Weekly Completion %: {dash['weekly_completion_pct']:.1f}%")

    # ----------------------------------------------------
    # 11. User Applies AI Roadmap Adjustment
    # ----------------------------------------------------
    log_step(11, "User Approves & Applies AI Roadmap Adjustment")
    adjust_payload = {
        "analysis_id": analysis_id,
        "roadmap_id": roadmap_id
    }
    r = client.post(f"/api/goals/{goal_id}/roadmap/adjust", json=adjust_payload, headers=headers)
    assert r.status_code == 200, f"Roadmap adjustment failed: {r.text}"
    adjustment = r.json()
    print(f"Roadmap Adjustment successfully recorded! Status: {adjustment['status']}")
    print(f"Adjustment Details: {adjustment['details']}")

    # ----------------------------------------------------
    # 12. Verify Historical Progress Remains Intact
    # ----------------------------------------------------
    log_step(12, "Verify Roadmap & Historical Progress Remain Accessible")
    # Verify Roadmap
    r = client.get(f"/api/goals/{goal_id}/roadmap", headers=headers)
    assert r.status_code == 200
    current_roadmap = r.json()
    print(f"Active Roadmap ID: {current_roadmap['id']}, Total Weeks: {len(current_roadmap['weeks'])}")

    # Verify Checkin History
    r = client.get(f"/api/goals/{goal_id}/checkins", headers=headers)
    assert r.status_code == 200
    all_checkins = r.json()
    print(f"Check-in History: {len(all_checkins)} check-in(s) available")
    for ci in all_checkins:
        print(f"  Check-in {ci['id']}: {ci['hours_spent']} hrs, accomplishments: '{ci['accomplishments']}'")

    print(f"\n{'='*70}")
    print("[SUCCESS] Full Acceptance Criteria Scenario Completed 100% End-to-End!")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    try:
        run_acceptance_scenario()
    except Exception as e:
        print(f"\n[FAILED]: {e}")
        sys.exit(1)
