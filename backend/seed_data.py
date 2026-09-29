"""
Seed data script for LevelUp AI.
Creates demo user, user preferences, and goals with realistic progress data.

Usage:
    python seed_data.py
    or
    python -m app.seed
"""
from app.seed import run_seed

if __name__ == "__main__":
    run_seed()
