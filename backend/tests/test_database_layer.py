import pytest
from datetime import date, datetime, timedelta, timezone
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.goal import Goal, GoalCategory, GoalPriority, GoalStatus
from app.models.roadmap import Roadmap, RoadmapWeek, Task, WeekStatus
from app.models.milestone import Milestone
from app.models.checkin import WeeklyCheckin, CheckinTask
from app.models.progress import ProgressRecord
from app.models.analysis import AIAnalysis, RoadmapAdjustment
from app.utils.security import get_password_hash, verify_password
from app.database import check_database_connection
from app.repositories.goal_repository import GoalRepository
from app.repositories.roadmap_repository import RoadmapRepository


def test_database_connection():
    """Verify database connection health check."""
    status = check_database_connection()
    assert status["connected"] is True
    assert status["status"] in ("ok", "healthy")


def test_user_creation_and_unique_email(db):
    """Test user creation and unique email constraint enforcement."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        name="Test User",
        email=unique_email,
        password_hash=get_password_hash("securepass123"),
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.email == unique_email
    assert verify_password("securepass123", user.password_hash)
    assert not verify_password("wrongpass", user.password_hash)

    # Attempt to insert identical email to verify unique constraint
    duplicate_user = User(
        name="Duplicate User",
        email=unique_email,
        password_hash=get_password_hash("anotherpass"),
    )
    db.add(duplicate_user)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_goal_creation_and_user_relationship(db):
    """Test goal creation and proper relationship to parent user."""
    user = User(
        name="Goal Owner",
        email=f"owner_{uuid.uuid4().hex[:8]}@example.com",
        password_hash=get_password_hash("pass123"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    goal = Goal(
        user_id=user.id,
        title="Master Algorithms",
        category=GoalCategory.coding,
        current_level="Beginner",
        target_outcome="Solve 100 LeetCode problems",
        start_date=date.today(),
        target_date=date.today() + timedelta(days=60),
        available_hours_per_week=8.0,
        progress_percentage=15.0,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)

    assert goal.id is not None
    assert goal.user_id == user.id
    assert goal.user.email == user.email
    assert goal.name == "Master Algorithms"  # Tests title/name synonym


def test_roadmap_milestone_task_hierarchy(db):
    """Test creation of Roadmap, RoadmapWeeks, Milestones, and Tasks."""
    user = User(name="Dev", email=f"dev_{uuid.uuid4().hex[:8]}@example.com")
    db.add(user)
    db.commit()

    goal = Goal(
        user_id=user.id,
        title="Web Development",
        category=GoalCategory.coding,
        current_level="Junior",
        target_outcome="Build production SaaS",
        start_date=date.today(),
        target_date=date.today() + timedelta(days=30),
        available_hours_per_week=10.0,
    )
    db.add(goal)
    db.commit()

    repo = RoadmapRepository(db)
    weeks_data = [
        {
            "week_number": 1,
            "title": "Database Architecture",
            "objective": "Design PostgreSQL schemas with Alembic",
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=6),
            "estimated_hours": 10.0,
            "tasks": [
                {"title": "Write models", "estimated_hours": 4.0, "priority": "high"},
                {"title": "Run migrations", "estimated_hours": 3.0, "priority": "high"},
            ]
        }
    ]
    milestones_data = [
        {"title": "DB Complete", "target_date": date.today() + timedelta(days=6)}
    ]

    roadmap = repo.create_roadmap_atomic(
        goal_id=goal.id,
        version=1,
        title="SaaS Dev Roadmap",
        weeks_data=weeks_data,
        milestones_data=milestones_data,
    )

    assert roadmap.id is not None
    assert len(roadmap.weeks) == 1
    assert len(roadmap.weeks[0].tasks) == 2
    assert len(roadmap.milestones) == 1
    assert roadmap.weeks[0].tasks[0].week_id == roadmap.weeks[0].id  # Tests synonym


def test_transaction_rollback_preserves_consistency(db):
    """Test that a transaction rollback cleanly restores database state on failure."""
    user = User(name="Rollback Tester", email=f"rb_{uuid.uuid4().hex[:8]}@example.com")
    db.add(user)
    db.commit()

    initial_goals_count = db.execute(select(Goal).where(Goal.user_id == user.id)).scalars().all()
    assert len(initial_goals_count) == 0

    try:
        # Step 1: Add a valid goal
        goal = Goal(
            user_id=user.id,
            title="Failed Transaction Goal",
            category=GoalCategory.fitness,
            current_level="Beginner",
            target_outcome="Test rollback",
            start_date=date.today(),
            target_date=date.today() + timedelta(days=10),
            available_hours_per_week=5.0,
        )
        db.add(goal)
        db.flush()

        # Step 2: Intentionally violate database constraint (title is NOT NULL)
        invalid_goal = Goal(
            user_id=user.id,
            title=None,
            category=GoalCategory.fitness,
            current_level="Beginner",
            target_outcome="Fail",
            start_date=date.today(),
            target_date=date.today() + timedelta(days=10),
            available_hours_per_week=5.0,
        )
        db.add(invalid_goal)
        db.commit()
    except Exception:
        db.rollback()

    # Verify that the entire transaction rolled back and the first goal was NOT committed
    remaining = db.execute(select(Goal).where(Goal.user_id == user.id)).scalars().all()
    assert len(remaining) == 0


def test_unauthorized_access_prevention(db):
    """Verify that GoalRepository prevents accessing another user's goals."""
    user_a = User(name="User A", email=f"user_a_{uuid.uuid4().hex[:8]}@example.com")
    user_b = User(name="User B", email=f"user_b_{uuid.uuid4().hex[:8]}@example.com")
    db.add_all([user_a, user_b])
    db.commit()

    goal_a = Goal(
        user_id=user_a.id,
        title="User A Private Goal",
        category=GoalCategory.academics,
        current_level="Beginner",
        target_outcome="Study",
        start_date=date.today(),
        target_date=date.today() + timedelta(days=14),
        available_hours_per_week=5.0,
    )
    db.add(goal_a)
    db.commit()

    repo = GoalRepository(db)

    # User A can access their own goal
    result_a = repo.get_by_id_and_user(goal_a.id, user_a.id)
    assert result_a is not None
    assert result_a.id == goal_a.id

    # User B CANNOT access User A's goal
    result_b = repo.get_by_id_and_user(goal_a.id, user_b.id)
    assert result_b is None, "Security violation: User B should not be able to access User A's goal"
