"""
Safe development seed script for LifeTrack AI.
Creates demo user, user preferences, goals, roadmaps, milestones, tasks,
weekly check-ins, progress records, and AI analyses in PostgreSQL.

Usage:
    python -m app.seed
    or
    python seed_data.py
"""
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date, datetime, timedelta, timezone
import uuid

from app.database import SessionLocal
from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.models.goal import Goal, GoalCategory, GoalPriority, GoalStatus
from app.models.roadmap import Roadmap, RoadmapWeek, Task, WeekStatus
from app.models.milestone import Milestone
from app.models.checkin import WeeklyCheckin, CheckinTask, DifficultyLevel
from app.models.progress import ProgressRecord
from app.models.analysis import AIAnalysis, RoadmapAdjustment, AdjustmentType, AdjustmentStatus
from app.utils.security import get_password_hash


def run_seed():
    print("[*] Connecting to PostgreSQL database and seeding development records...")
    db = SessionLocal()

    try:
        # Clean existing demo user transactionally without dropping schema tables
        existing_alex = db.query(User).filter(User.email == "alex@demo.com").first()
        if existing_alex:
            print("[*] Cleaning up previous demo records for alex@demo.com...")
            db.delete(existing_alex)
            db.commit()

        # 1. Demo User
        alex = User(
            name="Alex",
            email="alex@demo.com",
            password_hash=get_password_hash("password123"),
            email_verified=True,
            is_active=True,
            auth_provider="local",
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(alex)
        db.commit()
        db.refresh(alex)
        print(f"[OK] Created demo user: {alex.email} (id: {alex.id})")

        # 2. User Preferences
        prefs = UserPreferences(
            user_id=alex.id,
            preferred_days={"days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
            preferred_study_hours=2.5,
            timezone="America/New_York",
            notification_preferences={"weekly_digest": True, "checkin_reminders": True},
        )
        db.add(prefs)

        today = date.today()

        # 3. Goal 1: Learn Python & Data Structures (Coding)
        g1 = Goal(
            user_id=alex.id,
            title="Learn Python & Build Projects",
            category=GoalCategory.coding,
            description="Master Python fundamentals, data structures, and build two full-stack projects.",
            start_date=today - timedelta(days=21),
            target_date=today + timedelta(days=35),
            current_level="Beginner",
            target_outcome="Become comfortable with Python, OOP, APIs, and build 2 portfolio projects.",
            available_hours_per_week=10.0,
            priority=GoalPriority.high,
            status=GoalStatus.active,
            progress_percentage=65.0,
            motivation="To prepare for software engineering technical interviews and internships.",
            preferred_days={"days": ["Monday", "Wednesday", "Friday", "Saturday"]},
        )
        db.add(g1)
        db.flush()

        # Roadmap for Goal 1
        r1 = Roadmap(
            goal_id=g1.id,
            title="Python Mastery 8-Week Roadmap",
            description="Comprehensive path from syntax to full web project",
            version=1,
            status="active",
            is_active=True,
            generated_by="ai",
            generated_by_ai=True,
        )
        db.add(r1)
        db.flush()

        # Milestones for Goal 1
        m1 = Milestone(
            roadmap_id=r1.id,
            title="Core Python & Syntax Mastery",
            description="Complete control flow, functions, and data structures",
            target_date=today - timedelta(days=7),
            status="completed",
            completed_at=datetime.now(timezone.utc) - timedelta(days=7),
        )
        m2 = Milestone(
            roadmap_id=r1.id,
            title="Object-Oriented Programming & File I/O",
            description="Classes, inheritance, modules, error handling",
            target_date=today + timedelta(days=7),
            status="in_progress",
        )
        m3 = Milestone(
            roadmap_id=r1.id,
            title="Full Capstone Portfolio Project",
            description="FastAPI REST API with PostgreSQL and authentication",
            target_date=today + timedelta(days=35),
            status="pending",
        )
        db.add_all([m1, m2, m3])
        db.flush()

        # Weeks and Tasks for Goal 1
        w1_start = today - timedelta(days=21)
        w1 = RoadmapWeek(
            roadmap_id=r1.id,
            week_number=1,
            title="Python Fundamentals & Variables",
            objective="Master primitive types, expressions, conditionals, and standard library basics",
            start_date=w1_start,
            end_date=w1_start + timedelta(days=6),
            estimated_hours=10.0,
            status=WeekStatus.completed,
        )
        db.add(w1)
        db.flush()

        t1_1 = Task(
            roadmap_week_id=w1.id,
            milestone_id=m1.id,
            goal_id=g1.id,
            title="Install Python 3.12 and configure VS Code",
            estimated_hours=1.5,
            priority="high",
            status="completed",
            is_completed=True,
            order_index=1,
        )
        t1_2 = Task(
            roadmap_week_id=w1.id,
            milestone_id=m1.id,
            goal_id=g1.id,
            title="Variables, data types (int, float, str, bool), type casting",
            estimated_hours=2.5,
            priority="medium",
            status="completed",
            is_completed=True,
            order_index=2,
        )
        t1_3 = Task(
            roadmap_week_id=w1.id,
            milestone_id=m1.id,
            goal_id=g1.id,
            title="Control flow: if, elif, else, and logical operators",
            estimated_hours=3.0,
            priority="high",
            status="completed",
            is_completed=True,
            order_index=3,
        )
        t1_4 = Task(
            roadmap_week_id=w1.id,
            milestone_id=m1.id,
            goal_id=g1.id,
            title="Loops: for loops, while loops, break, and continue",
            estimated_hours=3.0,
            priority="high",
            status="completed",
            is_completed=True,
            order_index=4,
        )
        db.add_all([t1_1, t1_2, t1_3, t1_4])
        db.flush()

        # Checkin for Week 1
        c1 = WeeklyCheckin(
            user_id=alex.id,
            goal_id=g1.id,
            week_id=w1.id,
            week_start_date=w1_start,
            week_end_date=w1_start + timedelta(days=6),
            planned_hours=10.0,
            actual_hours=9.5,
            planned_tasks=4,
            completed_tasks=4,
            skipped_tasks=0,
            delayed_tasks=0,
            work_days_planned=5,
            work_days_completed=5,
            self_rating=8,
            accomplishments="Completed all core syntax exercises, built CLI calculator and temperature converter.",
            problems="Underestimated time needed for while loop edge cases.",
            difficulty="moderate",
            notes="Feeling confident heading into data structures.",
        )
        db.add(c1)
        db.flush()

        ct1_1 = CheckinTask(checkin_id=c1.id, task_id=t1_1.id, status="completed", hours_spent=1.5, is_completed=True)
        ct1_2 = CheckinTask(checkin_id=c1.id, task_id=t1_2.id, status="completed", hours_spent=2.5, is_completed=True)
        ct1_3 = CheckinTask(checkin_id=c1.id, task_id=t1_3.id, status="completed", hours_spent=2.5, is_completed=True)
        ct1_4 = CheckinTask(checkin_id=c1.id, task_id=t1_4.id, status="completed", hours_spent=3.0, is_completed=True)
        db.add_all([ct1_1, ct1_2, ct1_3, ct1_4])

        # Progress record for Week 1
        p1 = ProgressRecord(
            user_id=alex.id,
            goal_id=g1.id,
            recorded_date=w1_start + timedelta(days=6),
            week_number=1,
            task_completion_pct=100.0,
            time_completion_pct=95.0,
            consistency_pct=97.5,
            progress_percentage=97.5,
            completed_tasks=4,
            total_tasks=4,
            total_hours=9.5,
            streak_days=7,
            notes="Week 1 completed with exceptional consistency.",
        )
        db.add(p1)

        # AI Analysis for Week 1
        a1 = AIAnalysis(
            user_id=alex.id,
            goal_id=g1.id,
            checkin_id=c1.id,
            analysis_type="weekly_checkin",
            summary="Outstanding start to your Python journey. You hit 95% of your planned study hours and completed 100% of tasks.",
            what_went_well=["Hit 95% of target study hours", "Completed all 4 planned tasks on time", "Built CLI mini-projects ahead of schedule"],
            delayed_items=[],
            possible_reasons=[],
            recommendations=["Continue taking brief notes on list comprehensions", "Keep daily streak going by coding at least 45 minutes on weekdays"],
            next_week_focus=["Lists, dictionaries, and tuple unpacking", "Solving 5 LeetCode easy problems"],
            roadmap_adjustment_type="none",
            model_name="mock-ai",
        )
        db.add(a1)
        db.flush()

        # Goal 2: Physical Fitness & Strength Training (Fitness)
        g2 = Goal(
            user_id=alex.id,
            title="Consistent Strength & Endurance Training",
            category=GoalCategory.fitness,
            description="Work out 4 times a week, build functional strength, and run 5k in under 25 minutes.",
            start_date=today - timedelta(days=14),
            target_date=today + timedelta(days=70),
            current_level="Intermediate",
            target_outcome="Bench bodyweight, squat 1.5x bodyweight, run 5k consistently.",
            available_hours_per_week=6.0,
            priority=GoalPriority.medium,
            status=GoalStatus.active,
            progress_percentage=45.0,
            motivation="Improve energy levels, mental clarity, and athletic performance.",
            preferred_days={"days": ["Monday", "Wednesday", "Friday", "Sunday"]},
        )
        db.add(g2)
        db.flush()

        r2 = Roadmap(
            goal_id=g2.id,
            title="12-Week Functional Strength & 5K Protocol",
            version=1,
            status="active",
            is_active=True,
            generated_by="ai",
            generated_by_ai=True,
        )
        db.add(r2)

        # Commit everything safely
        db.commit()
        print(f"[OK] Seeded goals: '{g1.title}' and '{g2.title}' with complete roadmap, check-ins, progress, and AI analysis.")
        print("[OK] Database seeding finished successfully!")

    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
