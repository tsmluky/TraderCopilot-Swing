"""Ensure all missing tables exist (Scheduler, Audit, etc)

Revision ID: 999999999999
Revises: 888888888888
Create Date: 2026-01-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '999999999999'
down_revision = '888888888888'
branch_labels = None
depends_on = None

def table_exists(table_name):
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    return table_name in insp.get_table_names()

def upgrade():
    # 1. Scheduler Locks
    if not table_exists("scheduler_locks"):
        op.create_table(
            'scheduler_locks',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('lock_name', sa.String(), unique=True, index=True),
            sa.Column('acquired_at', sa.DateTime(), default=sa.func.now())
        )

    # 2. Strategy Configs
    if not table_exists("strategy_configs"):
        op.create_table(
            'strategy_configs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('strategy_id', sa.String()),
            sa.Column('persona_id', sa.String(128), index=True, nullable=True),
            sa.Column('name', sa.String(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('risk_profile', sa.String(), nullable=True),
            sa.Column('expected_roi', sa.String(), nullable=True),
            sa.Column('color', sa.String(), default="indigo"),
            sa.Column('icon', sa.String(), default="Zap"),
            sa.Column('is_public', sa.Integer(), default=0),
            sa.Column('enabled', sa.Integer(), default=1),
            sa.Column('total_signals', sa.Integer(), default=0),
            sa.Column('win_rate', sa.Float(), default=0.0),
            sa.Column('params_json', sa.Text(), nullable=True),
            sa.Column('tokens', sa.Text(), nullable=True),
            sa.Column('timeframes', sa.Text(), nullable=True),
            sa.UniqueConstraint("user_id", "persona_id", name="uq_user_persona")
        )

    # 3. Admin Audit Logs
    if not table_exists("admin_audit_logs"):
        op.create_table(
            'admin_audit_logs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('admin_id', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('action', sa.String()),
            sa.Column('target_id', sa.String()),
            sa.Column('details', sa.Text()),
            sa.Column('ip_address', sa.String(), nullable=True),
            sa.Column('timestamp', sa.DateTime(), default=sa.func.now())
        )

    # 4. Daily Usage
    if not table_exists("daily_usage"):
        op.create_table(
            'daily_usage',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('feature', sa.String()),
            sa.Column('date', sa.String()), # YYYY-MM-DD
            sa.Column('count', sa.Integer(), default=0),
            sa.UniqueConstraint("user_id", "feature", "date", name="uq_user_feature_date")
        )

    # 5. Copilot Profiles
    if not table_exists("copilot_profiles"):
        op.create_table(
            'copilot_profiles',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), unique=True, index=True),
            sa.Column('trader_style', sa.String(), default="BALANCED"),
            sa.Column('risk_tolerance', sa.String(), default="MODERATE"),
            sa.Column('time_horizon', sa.String(), default="SWING"),
            sa.Column('custom_instructions', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), default=sa.func.now())
        )

    # 6. Watch Alerts
    if not table_exists("watch_alerts"):
        op.create_table(
            'watch_alerts',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), index=True),
            sa.Column('token', sa.String(), index=True),
            sa.Column('timeframe', sa.String(), index=True),
            sa.Column('direction', sa.String(), nullable=True),
            sa.Column('condition', sa.Text(), nullable=True),
            sa.Column('enabled', sa.Integer(), default=1),
            sa.Column('created_at', sa.DateTime(), default=sa.func.now())
        )

    # 7. Push Subscriptions
    if not table_exists("push_subscriptions"):
        op.create_table(
            'push_subscriptions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
            sa.Column('endpoint', sa.Text()),
            sa.Column('p256dh', sa.Text()),
            sa.Column('auth', sa.Text()),
            sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
            sa.UniqueConstraint("user_id", "endpoint", name="uq_user_endpoint")
        )

def downgrade():
    # Only drop if they exist (safe downgrade) or strict?
    # Strict downgrade for consistency
    op.drop_table('push_subscriptions')
    op.drop_table('watch_alerts')
    op.drop_table('copilot_profiles')
    op.drop_table('daily_usage')
    op.drop_table('admin_audit_logs')
    op.drop_table('strategy_configs')
    op.drop_table('scheduler_locks')
