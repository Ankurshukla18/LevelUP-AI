"""initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-09-29 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ----------------------------------------------------
    # 1. users table
    # ----------------------------------------------------
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.Column('oauth_provider', sa.String(length=50), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=1024), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('verification_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_password_token', sa.String(length=255), nullable=True),
        sa.Column('reset_password_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_oauth_id', 'users', ['oauth_id'], unique=False)
    op.create_index('ix_users_oauth_provider', 'users', ['oauth_provider'], unique=False)
    op.create_index('ix_users_verification_token', 'users', ['verification_token'], unique=False)
    op.create_index('ix_users_reset_password_token', 'users', ['reset_password_token'], unique=False)

    # ----------------------------------------------------
    # 2. goals table
    # ----------------------------------------------------
    op.create_table(
        'goals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('current_level', sa.String(length=100), nullable=False),
        sa.Column('target_outcome', sa.Text(), nullable=False),
        sa.Column('available_hours_per_week', sa.Float(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('motivation', sa.Text(), nullable=True),
        sa.Column('preferred_days', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_goals_user_id', 'goals', ['user_id'], unique=False)
    op.create_index('ix_goals_category', 'goals', ['category'], unique=False)
    op.create_index('ix_goals_target_date', 'goals', ['target_date'], unique=False)
    op.create_index('ix_goals_status', 'goals', ['status'], unique=False)

    # ----------------------------------------------------
    # 3. roadmaps table
    # ----------------------------------------------------
    op.create_table(
        'roadmaps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('generated_by_ai', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roadmaps_goal_id', 'roadmaps', ['goal_id'], unique=False)
    op.create_index('ix_roadmaps_is_active', 'roadmaps', ['is_active'], unique=False)

    # ----------------------------------------------------
    # 4. roadmap_weeks table
    # ----------------------------------------------------
    op.create_table(
        'roadmap_weeks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('estimated_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='not_started'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_id'], ['roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('roadmap_id', 'week_number', name='uq_roadmap_week_number')
    )
    op.create_index('ix_roadmap_weeks_roadmap_id', 'roadmap_weeks', ['roadmap_id'], unique=False)
    op.create_index('ix_roadmap_weeks_status', 'roadmap_weeks', ['status'], unique=False)

    # ----------------------------------------------------
    # 5. tasks table
    # ----------------------------------------------------
    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('week_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['week_id'], ['roadmap_weeks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_week_id', 'tasks', ['week_id'], unique=False)
    op.create_index('ix_tasks_is_completed', 'tasks', ['is_completed'], unique=False)
    op.create_index('ix_tasks_week_order', 'tasks', ['week_id', 'order'], unique=False)

    # ----------------------------------------------------
    # 6. weekly_checkins table
    # ----------------------------------------------------
    op.create_table(
        'weekly_checkins',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('week_id', sa.UUID(), nullable=False),
        sa.Column('hours_spent', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('tasks_completed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tasks_skipped', sa.JSON(), nullable=True),
        sa.Column('accomplishments', sa.Text(), nullable=False),
        sa.Column('problems_faced', sa.Text(), nullable=True),
        sa.Column('difficulty_level', sa.String(length=30), nullable=False),
        sa.Column('self_rating', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['week_id'], ['roadmap_weeks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_weekly_checkins_goal_id', 'weekly_checkins', ['goal_id'], unique=False)
    op.create_index('ix_weekly_checkins_week_id', 'weekly_checkins', ['week_id'], unique=False)
    op.create_index('ix_weekly_checkins_goal_week', 'weekly_checkins', ['goal_id', 'week_id'], unique=False)
    op.create_index('ix_weekly_checkins_created_at', 'weekly_checkins', ['created_at'], unique=False)

    # ----------------------------------------------------
    # 7. checkin_tasks table
    # ----------------------------------------------------
    op.create_table(
        'checkin_tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('checkin_id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['checkin_id'], ['weekly_checkins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('checkin_id', 'task_id', name='uq_checkin_task')
    )
    op.create_index('ix_checkin_tasks_checkin_id', 'checkin_tasks', ['checkin_id'], unique=False)
    op.create_index('ix_checkin_tasks_task_id', 'checkin_tasks', ['task_id'], unique=False)

    # ----------------------------------------------------
    # 8. progress_records table
    # ----------------------------------------------------
    op.create_table(
        'progress_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('task_completion_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('time_completion_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('consistency_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_completed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_delayed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('goal_id', 'week_number', name='uq_progress_goal_week')
    )
    op.create_index('ix_progress_records_goal_id', 'progress_records', ['goal_id'], unique=False)
    op.create_index('ix_progress_records_goal_week', 'progress_records', ['goal_id', 'week_number'], unique=False)
    op.create_index('ix_progress_records_created_at', 'progress_records', ['created_at'], unique=False)

    # ----------------------------------------------------
    # 9. ai_analyses table
    # ----------------------------------------------------
    op.create_table(
        'ai_analyses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('checkin_id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('went_well', sa.JSON(), nullable=False),
        sa.Column('delayed', sa.JSON(), nullable=False),
        sa.Column('reasons', sa.JSON(), nullable=False),
        sa.Column('recommendations', sa.JSON(), nullable=False),
        sa.Column('next_week_focus', sa.JSON(), nullable=False),
        sa.Column('roadmap_adjustment_type', sa.String(length=30), nullable=False, server_default='none'),
        sa.Column('adjustment_details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['checkin_id'], ['weekly_checkins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_analyses_checkin_id', 'ai_analyses', ['checkin_id'], unique=False)
    op.create_index('ix_ai_analyses_goal_id', 'ai_analyses', ['goal_id'], unique=False)
    op.create_index('ix_ai_analyses_goal_created', 'ai_analyses', ['goal_id', 'created_at'], unique=False)
    op.create_index('ix_ai_analyses_created_at', 'ai_analyses', ['created_at'], unique=False)

    # ----------------------------------------------------
    # 10. roadmap_adjustments table
    # ----------------------------------------------------
    op.create_table(
        'roadmap_adjustments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('analysis_id', sa.UUID(), nullable=False),
        sa.Column('adjustment_type', sa.String(length=50), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_id'], ['roadmaps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['analysis_id'], ['ai_analyses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roadmap_adjustments_roadmap_id', 'roadmap_adjustments', ['roadmap_id'], unique=False)
    op.create_index('ix_roadmap_adjustments_analysis_id', 'roadmap_adjustments', ['analysis_id'], unique=False)
    op.create_index('ix_roadmap_adjustments_status', 'roadmap_adjustments', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse topological order
    op.drop_table('roadmap_adjustments')
    op.drop_table('ai_analyses')
    op.drop_table('progress_records')
    op.drop_table('checkin_tasks')
    op.drop_table('weekly_checkins')
    op.drop_table('tasks')
    op.drop_table('roadmap_weeks')
    op.drop_table('roadmaps')
    op.drop_table('goals')
    op.drop_table('users')
