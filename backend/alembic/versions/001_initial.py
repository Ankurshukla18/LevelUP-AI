"""complete_initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-09-29 10:30:00.000000

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
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('google_id', sa.String(length=255), nullable=True),
        sa.Column('profile_picture', sa.String(length=1024), nullable=True),
        sa.Column('auth_provider', sa.String(length=50), nullable=False, server_default='local'),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_token', sa.String(length=255), nullable=True),
        sa.Column('verification_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reset_password_token', sa.String(length=255), nullable=True),
        sa.Column('reset_password_token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)
    op.create_index('ix_users_auth_provider', 'users', ['auth_provider'], unique=False)
    op.create_index('ix_users_verification_token', 'users', ['verification_token'], unique=False)
    op.create_index('ix_users_reset_password_token', 'users', ['reset_password_token'], unique=False)

    # ----------------------------------------------------
    # 2. user_preferences table
    # ----------------------------------------------------
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('preferred_days', sa.JSON(), nullable=True),
        sa.Column('preferred_study_hours', sa.Float(), nullable=True),
        sa.Column('timezone', sa.String(length=100), nullable=False, server_default='UTC'),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_user_preferences_user_id')
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)

    # ----------------------------------------------------
    # 3. goals table
    # ----------------------------------------------------
    op.create_table(
        'goals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('current_level', sa.String(length=100), nullable=False),
        sa.Column('target_outcome', sa.Text(), nullable=False),
        sa.Column('available_hours_per_week', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('motivation', sa.Text(), nullable=True),
        sa.Column('preferred_days', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='ck_goals_progress_percentage'),
        sa.CheckConstraint('available_hours_per_week >= 0', name='ck_goals_available_hours'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_goals_user_id', 'goals', ['user_id'], unique=False)
    op.create_index('ix_goals_category', 'goals', ['category'], unique=False)
    op.create_index('ix_goals_target_date', 'goals', ['target_date'], unique=False)
    op.create_index('ix_goals_status', 'goals', ['status'], unique=False)
    op.create_index('ix_goals_user_status', 'goals', ['user_id', 'status'], unique=False)
    op.create_index('ix_goals_category_status', 'goals', ['category', 'status'], unique=False)

    # ----------------------------------------------------
    # 4. roadmaps table
    # ----------------------------------------------------
    op.create_table(
        'roadmaps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Roadmap'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('generated_by', sa.String(length=50), nullable=False, server_default='ai'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('generated_by_ai', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roadmaps_goal_id', 'roadmaps', ['goal_id'], unique=False)
    op.create_index('ix_roadmaps_status', 'roadmaps', ['status'], unique=False)
    op.create_index('ix_roadmaps_is_active', 'roadmaps', ['is_active'], unique=False)
    op.create_index('ix_roadmaps_goal_status', 'roadmaps', ['goal_id', 'status'], unique=False)

    # ----------------------------------------------------
    # 5. roadmap_weeks table
    # ----------------------------------------------------
    op.create_table(
        'roadmap_weeks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('objective', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('estimated_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='not_started'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('estimated_hours >= 0', name='ck_roadmap_weeks_estimated_hours'),
        sa.ForeignKeyConstraint(['roadmap_id'], ['roadmaps.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('roadmap_id', 'week_number', name='uq_roadmap_week_number')
    )
    op.create_index('ix_roadmap_weeks_roadmap_id', 'roadmap_weeks', ['roadmap_id'], unique=False)
    op.create_index('ix_roadmap_weeks_status', 'roadmap_weeks', ['status'], unique=False)

    # ----------------------------------------------------
    # 6. milestones table
    # ----------------------------------------------------
    op.create_table(
        'milestones',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('week_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_id'], ['roadmaps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['week_id'], ['roadmap_weeks.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_milestones_roadmap_id', 'milestones', ['roadmap_id'], unique=False)
    op.create_index('ix_milestones_week_id', 'milestones', ['week_id'], unique=False)
    op.create_index('ix_milestones_status', 'milestones', ['status'], unique=False)
    op.create_index('ix_milestones_roadmap_status', 'milestones', ['roadmap_id', 'status'], unique=False)

    # ----------------------------------------------------
    # 7. tasks table
    # ----------------------------------------------------
    op.create_table(
        'tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('roadmap_week_id', sa.UUID(), nullable=False),
        sa.Column('milestone_id', sa.UUID(), nullable=True),
        sa.Column('goal_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='medium'),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('estimated_hours IS NULL OR estimated_hours >= 0', name='ck_tasks_estimated_hours'),
        sa.ForeignKeyConstraint(['roadmap_week_id'], ['roadmap_weeks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['milestone_id'], ['milestones.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tasks_roadmap_week_id', 'tasks', ['roadmap_week_id'], unique=False)
    op.create_index('ix_tasks_goal_id', 'tasks', ['goal_id'], unique=False)
    op.create_index('ix_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('ix_tasks_due_date', 'tasks', ['due_date'], unique=False)
    op.create_index('ix_tasks_is_completed', 'tasks', ['is_completed'], unique=False)
    op.create_index('ix_tasks_week_order', 'tasks', ['roadmap_week_id', 'order_index'], unique=False)

    # ----------------------------------------------------
    # 8. weekly_checkins table
    # ----------------------------------------------------
    op.create_table(
        'weekly_checkins',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('week_id', sa.UUID(), nullable=False),
        sa.Column('week_start_date', sa.Date(), nullable=True),
        sa.Column('week_end_date', sa.Date(), nullable=True),
        sa.Column('planned_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('actual_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('planned_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('skipped_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delayed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('work_days_planned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('work_days_completed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('self_rating', sa.Integer(), nullable=False),
        sa.Column('accomplishments', sa.Text(), nullable=False),
        sa.Column('problems', sa.Text(), nullable=True),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='moderate'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tasks_skipped', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('self_rating >= 1 AND self_rating <= 10', name='ck_weekly_checkin_self_rating'),
        sa.CheckConstraint('actual_hours >= 0', name='ck_weekly_checkin_actual_hours'),
        sa.CheckConstraint('planned_hours >= 0', name='ck_weekly_checkin_planned_hours'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['week_id'], ['roadmap_weeks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_weekly_checkins_user_id', 'weekly_checkins', ['user_id'], unique=False)
    op.create_index('ix_weekly_checkins_goal_id', 'weekly_checkins', ['goal_id'], unique=False)
    op.create_index('ix_weekly_checkins_week_id', 'weekly_checkins', ['week_id'], unique=False)
    op.create_index('ix_weekly_checkins_week_start', 'weekly_checkins', ['week_start_date'], unique=False)
    op.create_index('ix_weekly_checkins_goal_week', 'weekly_checkins', ['goal_id', 'week_id'], unique=False)

    # ----------------------------------------------------
    # 9. checkin_tasks table
    # ----------------------------------------------------
    op.create_table(
        'checkin_tasks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('checkin_id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('hours_spent', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('hours_spent >= 0', name='ck_checkin_task_hours_spent'),
        sa.ForeignKeyConstraint(['checkin_id'], ['weekly_checkins.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('checkin_id', 'task_id', name='uq_checkin_task')
    )
    op.create_index('ix_checkin_tasks_checkin_id', 'checkin_tasks', ['checkin_id'], unique=False)
    op.create_index('ix_checkin_tasks_task_id', 'checkin_tasks', ['task_id'], unique=False)

    # ----------------------------------------------------
    # 10. progress_records table
    # ----------------------------------------------------
    op.create_table(
        'progress_records',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('recorded_date', sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('consistency_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('completed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_delayed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('streak_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('task_completion_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('time_completion_pct', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('progress_percentage >= 0 AND progress_percentage <= 100', name='ck_progress_percentage'),
        sa.CheckConstraint('consistency_percentage >= 0 AND consistency_percentage <= 100', name='ck_consistency_percentage'),
        sa.CheckConstraint('total_hours >= 0', name='ck_progress_total_hours'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('goal_id', 'week_number', name='uq_progress_goal_week')
    )
    op.create_index('ix_progress_records_user_id', 'progress_records', ['user_id'], unique=False)
    op.create_index('ix_progress_records_goal_id', 'progress_records', ['goal_id'], unique=False)
    op.create_index('ix_progress_records_recorded_date', 'progress_records', ['recorded_date'], unique=False)
    op.create_index('ix_progress_records_goal_week', 'progress_records', ['goal_id', 'week_number'], unique=False)

    # ----------------------------------------------------
    # 11. ai_analyses table
    # ----------------------------------------------------
    op.create_table(
        'ai_analyses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('goal_id', sa.UUID(), nullable=False),
        sa.Column('checkin_id', sa.UUID(), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False, server_default='weekly_checkin'),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('what_went_well', sa.JSON(), nullable=False),
        sa.Column('delayed_items', sa.JSON(), nullable=False),
        sa.Column('possible_reasons', sa.JSON(), nullable=False),
        sa.Column('recommendations', sa.JSON(), nullable=False),
        sa.Column('next_week_focus', sa.JSON(), nullable=False),
        sa.Column('roadmap_adjustment_type', sa.String(length=50), nullable=False, server_default='none'),
        sa.Column('roadmap_adjustment_suggestion', sa.JSON(), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False, server_default='mock-ai'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['checkin_id'], ['weekly_checkins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_analyses_user_id', 'ai_analyses', ['user_id'], unique=False)
    op.create_index('ix_ai_analyses_goal_id', 'ai_analyses', ['goal_id'], unique=False)
    op.create_index('ix_ai_analyses_checkin_id', 'ai_analyses', ['checkin_id'], unique=False)
    op.create_index('ix_ai_analyses_type', 'ai_analyses', ['analysis_type'], unique=False)
    op.create_index('ix_ai_analyses_goal_created', 'ai_analyses', ['goal_id', 'created_at'], unique=False)

    # ----------------------------------------------------
    # 12. roadmap_adjustments table
    # ----------------------------------------------------
    op.create_table(
        'roadmap_adjustments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('goal_id', sa.UUID(), nullable=True),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('ai_analysis_id', sa.UUID(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=False),
        sa.Column('adjustment_type', sa.String(length=50), nullable=False, server_default='reduce'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['roadmap_id'], ['roadmaps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ai_analysis_id'], ['ai_analyses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roadmap_adjustments_user_id', 'roadmap_adjustments', ['user_id'], unique=False)
    op.create_index('ix_roadmap_adjustments_goal_id', 'roadmap_adjustments', ['goal_id'], unique=False)
    op.create_index('ix_roadmap_adjustments_roadmap_id', 'roadmap_adjustments', ['roadmap_id'], unique=False)
    op.create_index('ix_roadmap_adjustments_status', 'roadmap_adjustments', ['status'], unique=False)
    op.create_index('ix_roadmap_adjustments_goal_status', 'roadmap_adjustments', ['goal_id', 'status'], unique=False)


def downgrade() -> None:
    op.drop_table('roadmap_adjustments')
    op.drop_table('ai_analyses')
    op.drop_table('progress_records')
    op.drop_table('checkin_tasks')
    op.drop_table('weekly_checkins')
    op.drop_table('tasks')
    op.drop_table('milestones')
    op.drop_table('roadmap_weeks')
    op.drop_table('roadmaps')
    op.drop_table('goals')
    op.drop_table('user_preferences')
    op.drop_table('users')
