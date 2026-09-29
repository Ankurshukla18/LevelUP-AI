"""
Seed data script for LifeTrack AI.
Creates demo user and goals with realistic progress data.

Usage:
    python seed_data.py
"""
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.goal import Goal, GoalCategory, GoalPriority, GoalStatus
from app.models.roadmap import Roadmap, RoadmapWeek, Task, WeekStatus
from app.models.checkin import WeeklyCheckin, CheckinTask, DifficultyLevel
from app.models.progress import ProgressRecord
from app.models.analysis import AIAnalysis, AdjustmentType
from app.utils.security import get_password_hash
from datetime import date, timedelta
import uuid


def seed():
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ──────────────────────────────────────────────────
        # User
        # ──────────────────────────────────────────────────
        alex = User(
            email="alex@demo.com",
            name="Alex",
            hashed_password=get_password_hash("password123"),
        )
        db.add(alex)
        db.commit()
        db.refresh(alex)
        print(f"Created user: {alex.email}")

        today = date.today()

        # ──────────────────────────────────────────────────
        # Goal 1: Learn Python
        # ──────────────────────────────────────────────────
        g1 = Goal(
            user_id=alex.id,
            name="Learn Python",
            category=GoalCategory.coding,
            description="Learn Python from scratch and build two projects",
            start_date=today - timedelta(days=21),
            target_date=today + timedelta(days=35),
            current_level="Beginner",
            target_outcome="Become comfortable with Python and build 2 projects",
            available_hours_per_week=8.0,
            priority=GoalPriority.high,
            motivation="Want to become a software developer",
            status=GoalStatus.active,
        )
        # Goal 2: Improve DSA
        g2 = Goal(
            user_id=alex.id,
            name="Improve DSA",
            category=GoalCategory.academics,
            description="Master data structures and algorithms for interviews",
            start_date=today - timedelta(days=14),
            target_date=today + timedelta(days=56),
            current_level="Intermediate",
            target_outcome="Solve medium LeetCode problems consistently",
            available_hours_per_week=5.0,
            priority=GoalPriority.medium,
            motivation="Preparing for technical interviews",
            status=GoalStatus.active,
        )
        # Goal 3: Increase Bench Press
        g3 = Goal(
            user_id=alex.id,
            name="Increase Bench Press",
            category=GoalCategory.fitness,
            description="Progressive overload program for bench press",
            start_date=today - timedelta(days=7),
            target_date=today + timedelta(days=77),
            current_level="135 lbs",
            target_outcome="185 lbs bench press",
            available_hours_per_week=4.0,
            priority=GoalPriority.medium,
            motivation="Personal fitness goal",
            status=GoalStatus.active,
        )
        db.add_all([g1, g2, g3])
        db.commit()
        for g in [g1, g2, g3]:
            db.refresh(g)
        print(f"Created goals: {g1.name}, {g2.name}, {g3.name}")

        # ──────────────────────────────────────────────────
        # Roadmap for Goal 1: Learn Python (8 weeks)
        # ──────────────────────────────────────────────────
        r1 = Roadmap(goal_id=g1.id, version=1, is_active=True, generated_by_ai=True)
        db.add(r1)
        db.commit()
        db.refresh(r1)

        python_weeks = [
            {
                "num": 1,
                "title": "Python Fundamentals",
                "desc": "Variables, data types, operators, and I/O",
                "hours": 8.0,
                "status": WeekStatus.completed,
                "tasks": [
                    ("Install Python & IDE setup", 1.0, True),
                    ("Variables and data types", 2.0, True),
                    ("Operators and expressions", 1.5, True),
                    ("Input/output operations", 1.5, True),
                    ("String operations", 2.0, True),
                ],
            },
            {
                "num": 2,
                "title": "Control Flow",
                "desc": "Conditions, loops, and practice problems",
                "hours": 8.0,
                "status": WeekStatus.completed,
                "tasks": [
                    ("If/elif/else conditions", 2.0, True),
                    ("For loops", 1.5, True),
                    ("While loops", 1.5, True),
                    ("Nested loops", 1.0, True),
                    ("Practice: 10 loop problems", 2.0, False),
                ],
            },
            {
                "num": 3,
                "title": "Functions & Modules",
                "desc": "Functions, arguments, return values, modules",
                "hours": 8.0,
                "status": WeekStatus.in_progress,
                "tasks": [
                    ("Function definitions", 2.0, True),
                    ("Parameters and return values", 1.5, True),
                    ("Lambda functions", 1.0, False),
                    ("Built-in modules", 1.5, False),
                    ("Create your own module", 2.0, False),
                ],
            },
            {
                "num": 4,
                "title": "Data Structures",
                "desc": "Lists, dictionaries, sets, tuples",
                "hours": 8.0,
                "status": WeekStatus.not_started,
                "tasks": [
                    ("Lists and list comprehensions", 2.0, False),
                    ("Dictionaries", 2.0, False),
                    ("Sets and tuples", 1.5, False),
                    ("Nested data structures", 1.5, False),
                    ("Practice problems", 1.0, False),
                ],
            },
            {
                "num": 5,
                "title": "File I/O & Exceptions",
                "desc": "File handling and error management",
                "hours": 8.0,
                "status": WeekStatus.not_started,
                "tasks": [
                    ("Reading and writing files", 2.0, False),
                    ("CSV and JSON handling", 2.0, False),
                    ("Try/except blocks", 1.5, False),
                    ("Custom exceptions", 1.5, False),
                    ("Practice project: Log parser", 1.0, False),
                ],
            },
            {
                "num": 6,
                "title": "Object-Oriented Programming",
                "desc": "Classes, inheritance, polymorphism",
                "hours": 8.0,
                "status": WeekStatus.not_started,
                "tasks": [
                    ("Classes and objects", 2.0, False),
                    ("Inheritance", 2.0, False),
                    ("Encapsulation & polymorphism", 2.0, False),
                    ("Practice: Build a class hierarchy", 2.0, False),
                ],
            },
            {
                "num": 7,
                "title": "Project 1: CLI Application",
                "desc": "Build a command-line task manager",
                "hours": 8.0,
                "status": WeekStatus.not_started,
                "tasks": [
                    ("Project planning & design", 1.5, False),
                    ("Core functionality", 3.0, False),
                    ("File persistence", 2.0, False),
                    ("Error handling & polish", 1.5, False),
                ],
            },
            {
                "num": 8,
                "title": "Project 2: Web Scraper",
                "desc": "Build a web scraper with requests & BeautifulSoup",
                "hours": 8.0,
                "status": WeekStatus.not_started,
                "tasks": [
                    ("Learn requests library", 1.5, False),
                    ("Learn BeautifulSoup", 2.0, False),
                    ("Build scraper", 3.0, False),
                    ("Data export & documentation", 1.5, False),
                ],
            },
        ]

        week_models = []
        for wdata in python_weeks:
            start = g1.start_date + timedelta(days=7 * (wdata["num"] - 1))
            end = start + timedelta(days=6)
            week = RoadmapWeek(
                roadmap_id=r1.id,
                week_number=wdata["num"],
                title=wdata["title"],
                description=wdata["desc"],
                start_date=start,
                end_date=end,
                estimated_hours=wdata["hours"],
                status=wdata["status"],
            )
            db.add(week)
            db.commit()
            db.refresh(week)
            week_models.append(week)

            for idx, (task_title, task_hours, completed) in enumerate(wdata["tasks"]):
                task = Task(
                    week_id=week.id,
                    title=task_title,
                    estimated_hours=task_hours,
                    is_completed=completed,
                    order=idx + 1,
                )
                db.add(task)
            db.commit()

        print(f"Created roadmap for {g1.name} with {len(python_weeks)} weeks")

        # ──────────────────────────────────────────────────
        # Check-ins for Goal 1
        # ──────────────────────────────────────────────────
        # Week 1 check-in
        w1_tasks = db.query(Task).filter(Task.week_id == week_models[0].id).all()
        c1 = WeeklyCheckin(
            goal_id=g1.id,
            week_id=week_models[0].id,
            hours_spent=7.5,
            tasks_completed_count=5,
            accomplishments="Completed all fundamentals. Python syntax is intuitive.",
            problems_faced="None significant, IDE setup took longer than expected.",
            difficulty_level=DifficultyLevel.easy,
            self_rating=8,
            notes="Great start!",
        )
        db.add(c1)
        db.commit()
        db.refresh(c1)
        for t in w1_tasks:
            ct = CheckinTask(checkin_id=c1.id, task_id=t.id, is_completed=t.is_completed)
            db.add(ct)
        db.commit()

        # Week 2 check-in
        w2_tasks = db.query(Task).filter(Task.week_id == week_models[1].id).all()
        c2 = WeeklyCheckin(
            goal_id=g1.id,
            week_id=week_models[1].id,
            hours_spent=6.5,
            tasks_completed_count=4,
            accomplishments="Understood conditions and loops well.",
            problems_faced="Nested loops were confusing. Didn't finish all practice problems.",
            difficulty_level=DifficultyLevel.moderate,
            self_rating=7,
            notes="Need more loop practice",
        )
        db.add(c2)
        db.commit()
        db.refresh(c2)
        for t in w2_tasks:
            ct = CheckinTask(checkin_id=c2.id, task_id=t.id, is_completed=t.is_completed)
            db.add(ct)
        db.commit()

        # Week 3 check-in (partial - current week)
        w3_tasks = db.query(Task).filter(Task.week_id == week_models[2].id).all()
        c3 = WeeklyCheckin(
            goal_id=g1.id,
            week_id=week_models[2].id,
            hours_spent=4.0,
            tasks_completed_count=2,
            accomplishments="Started functions, parameters make sense now.",
            problems_faced="Lambda functions are confusing.",
            difficulty_level=DifficultyLevel.moderate,
            self_rating=6,
        )
        db.add(c3)
        db.commit()
        db.refresh(c3)
        for t in w3_tasks:
            ct = CheckinTask(checkin_id=c3.id, task_id=t.id, is_completed=t.is_completed)
            db.add(ct)
        db.commit()

        print(f"Created {3} check-ins for {g1.name}")

        # ──────────────────────────────────────────────────
        # Progress Records for Goal 1
        # ──────────────────────────────────────────────────
        pr1 = ProgressRecord(
            goal_id=g1.id,
            week_number=1,
            task_completion_pct=100.0,
            time_completion_pct=93.75,
            consistency_pct=96.88,
            total_completed_tasks=5,
            total_delayed_tasks=0,
            total_hours=7.5,
            streak=1,
        )
        pr2 = ProgressRecord(
            goal_id=g1.id,
            week_number=2,
            task_completion_pct=80.0,
            time_completion_pct=81.25,
            consistency_pct=80.63,
            total_completed_tasks=4,
            total_delayed_tasks=1,
            total_hours=6.5,
            streak=2,
        )
        pr3 = ProgressRecord(
            goal_id=g1.id,
            week_number=3,
            task_completion_pct=40.0,
            time_completion_pct=50.0,
            consistency_pct=45.0,
            total_completed_tasks=2,
            total_delayed_tasks=3,
            total_hours=4.0,
            streak=3,
        )
        db.add_all([pr1, pr2, pr3])
        db.commit()
        print(f"Created progress records for {g1.name}")

        # ──────────────────────────────────────────────────
        # AI Analyses for Goal 1
        # ──────────────────────────────────────────────────
        a1 = AIAnalysis(
            checkin_id=c1.id,
            goal_id=g1.id,
            summary="Excellent first week! You completed all planned tasks and stayed close to your hour target. Strong foundation established.",
            went_well=["Completed all 5 tasks", "Good time management", "Python basics well understood"],
            delayed=[],
            reasons=[],
            recommendations=[
                "Continue at this pace",
                "Start looking ahead at Week 2 topics",
                "Try writing small programs daily",
            ],
            next_week_focus=["Master if/elif/else", "Practice for loops", "Start while loops"],
            roadmap_adjustment_type=AdjustmentType.none,
        )
        a2 = AIAnalysis(
            checkin_id=c2.id,
            goal_id=g1.id,
            summary="Good progress on control flow. Missed practice problems due to nested loops difficulty. Consider extra practice time next week.",
            went_well=[
                "Conditions understood well",
                "For loops mastered",
                "Consistent study schedule",
            ],
            delayed=["Practice: 10 loop problems"],
            reasons=[
                "Nested loops required more time than estimated",
                "Underestimated complexity of practice set",
            ],
            recommendations=[
                "Allocate 30 min/day for loop practice",
                "Use visual debugger to trace loop execution",
                "Revisit nested loops before moving to functions",
            ],
            next_week_focus=[
                "Complete remaining loop problems",
                "Start function definitions",
                "Practice with parameters and return values",
            ],
            roadmap_adjustment_type=AdjustmentType.reorder,
            adjustment_details={
                "action": "Move remaining loop problems to beginning of Week 3",
                "reason": "Ensure strong foundation before functions",
            },
        )
        a3 = AIAnalysis(
            checkin_id=c3.id,
            goal_id=g1.id,
            summary="Week 3 is showing a slowdown. Only 40% tasks completed with 50% hours used. Lambda functions are causing difficulty. Consider redistributing workload.",
            went_well=["Function definitions understood", "Parameters and return values grasped"],
            delayed=["Lambda functions", "Built-in modules", "Create your own module"],
            reasons=[
                "Lambda syntax is abstract for beginners",
                "May need more time on core function concepts first",
            ],
            recommendations=[
                "Focus on understanding regular functions deeply first",
                "Move lambda functions to a later week",
                "Reduce this week's scope and catch up next week",
            ],
            next_week_focus=[
                "Complete lambda functions with simple examples",
                "Explore 3 built-in modules (os, math, random)",
                "Create a small utility module",
            ],
            roadmap_adjustment_type=AdjustmentType.reduce,
            adjustment_details={
                "action": "Reduce Week 3 scope, carry over to Week 4",
                "affected_tasks": ["Lambda functions", "Create your own module"],
            },
        )
        db.add_all([a1, a2, a3])
        db.commit()
        print(f"Created AI analyses for {g1.name}")

        # ──────────────────────────────────────────────────
        # Roadmap for Goal 2: Improve DSA (abbreviated)
        # ──────────────────────────────────────────────────
        r2 = Roadmap(goal_id=g2.id, version=1, is_active=True, generated_by_ai=True)
        db.add(r2)
        db.commit()
        db.refresh(r2)

        dsa_weeks = [
            ("Arrays & Strings", "Array manipulation, string problems", 5.0, WeekStatus.completed),
            ("Linked Lists", "Singly and doubly linked lists", 5.0, WeekStatus.in_progress),
            ("Stacks & Queues", "Stack and queue implementations", 5.0, WeekStatus.not_started),
            ("Trees & BST", "Binary trees, BST operations", 5.0, WeekStatus.not_started),
            ("Graphs", "BFS, DFS, shortest path", 5.0, WeekStatus.not_started),
            ("Dynamic Programming", "Memoization, tabulation", 5.0, WeekStatus.not_started),
            ("Sorting & Searching", "Advanced sorting, binary search", 5.0, WeekStatus.not_started),
            ("Mock Interviews", "Practice with timed problems", 5.0, WeekStatus.not_started),
        ]
        for i, (title, desc, hours, status) in enumerate(dsa_weeks, 1):
            start = g2.start_date + timedelta(days=7 * (i - 1))
            w = RoadmapWeek(
                roadmap_id=r2.id,
                week_number=i,
                title=title,
                description=desc,
                start_date=start,
                end_date=start + timedelta(days=6),
                estimated_hours=hours,
                status=status,
            )
            db.add(w)
            db.commit()
            db.refresh(w)

            tasks = [
                (f"Study {title} theory", 1.5, status == WeekStatus.completed),
                (f"Solve 5 easy problems", 1.5, status == WeekStatus.completed),
                (f"Solve 3 medium problems", 2.0, False),
            ]
            for idx, (tt, th, tc) in enumerate(tasks):
                db.add(Task(week_id=w.id, title=tt, estimated_hours=th, is_completed=tc, order=idx + 1))
            db.commit()

        print(f"Created roadmap for {g2.name} with {len(dsa_weeks)} weeks")

        # DSA check-in & progress
        dsa_w1 = db.query(RoadmapWeek).filter(
            RoadmapWeek.roadmap_id == r2.id, RoadmapWeek.week_number == 1
        ).first()
        dsa_c1 = WeeklyCheckin(
            goal_id=g2.id,
            week_id=dsa_w1.id,
            hours_spent=4.5,
            tasks_completed_count=2,
            accomplishments="Completed array theory and easy problems. Two-pointer technique is useful.",
            problems_faced="Medium problems took too long.",
            difficulty_level=DifficultyLevel.hard,
            self_rating=6,
        )
        db.add(dsa_c1)
        db.commit()
        db.refresh(dsa_c1)

        dsa_pr1 = ProgressRecord(
            goal_id=g2.id,
            week_number=1,
            task_completion_pct=66.7,
            time_completion_pct=90.0,
            consistency_pct=78.35,
            total_completed_tasks=2,
            total_delayed_tasks=1,
            total_hours=4.5,
            streak=1,
        )
        db.add(dsa_pr1)
        db.commit()

        # ──────────────────────────────────────────────────
        # Roadmap for Goal 3: Fitness (abbreviated)
        # ──────────────────────────────────────────────────
        r3 = Roadmap(goal_id=g3.id, version=1, is_active=True, generated_by_ai=True)
        db.add(r3)
        db.commit()
        db.refresh(r3)

        fitness_weeks = [
            ("Foundation Phase", "Establish baseline and form", 4.0, WeekStatus.completed),
            ("Volume Build", "Increase training volume", 4.0, WeekStatus.not_started),
            ("Strength Focus", "Heavy sets and progressive overload", 4.0, WeekStatus.not_started),
            ("Deload & Recovery", "Active recovery week", 2.0, WeekStatus.not_started),
        ]
        for i, (title, desc, hours, status) in enumerate(fitness_weeks, 1):
            start = g3.start_date + timedelta(days=7 * (i - 1))
            w = RoadmapWeek(
                roadmap_id=r3.id,
                week_number=i,
                title=title,
                description=desc,
                start_date=start,
                end_date=start + timedelta(days=6),
                estimated_hours=hours,
                status=status,
            )
            db.add(w)
            db.commit()
            db.refresh(w)

            tasks = [
                (f"Workout Session 1", 1.0, status == WeekStatus.completed),
                (f"Workout Session 2", 1.0, status == WeekStatus.completed),
                (f"Workout Session 3", 1.0, status == WeekStatus.completed),
                (f"Track metrics & nutrition", 1.0, False),
            ]
            for idx, (tt, th, tc) in enumerate(tasks):
                db.add(Task(week_id=w.id, title=tt, estimated_hours=th, is_completed=tc, order=idx + 1))
            db.commit()

        print(f"Created roadmap for {g3.name} with {len(fitness_weeks)} weeks")

        db.close()
        print("\n[SUCCESS] Seed data populated successfully!")
        print("Demo login: alex@demo.com / password123")

    except Exception as e:
        db.rollback()
        db.close()
        print(f"\n[ERROR] Error seeding data: {e}")
        raise


if __name__ == "__main__":
    seed()
