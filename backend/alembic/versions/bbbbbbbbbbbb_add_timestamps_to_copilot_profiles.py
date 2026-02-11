"""add_timestamps_to_copilot_profiles

Revision ID: bbbbbbbbbbbb
Revises: aaaaaaaaaaaa
Create Date: 2026-01-27 21:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'bbbbbbbbbbbb'
down_revision = 'aaaaaaaaaaaa'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    columns = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in columns

def upgrade():
    # Add created_at and updated_at columns to copilot_profiles if they don't exist
    if not column_exists('copilot_profiles', 'created_at'):
        op.add_column('copilot_profiles', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    if not column_exists('copilot_profiles', 'updated_at'):
        op.add_column('copilot_profiles', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Optional: Backfill existing rows with current time (idempotent query)
    op.execute("UPDATE copilot_profiles SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE copilot_profiles SET updated_at = NOW() WHERE updated_at IS NULL")


def downgrade():
    op.drop_column('copilot_profiles', 'updated_at')
    op.drop_column('copilot_profiles', 'created_at')
