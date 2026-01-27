"""add_timestamps_to_copilot_profiles

Revision ID: bbbbbbbbbbbb
Revises: aaaaaaaaaaaa
Create Date: 2026-01-27 21:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'bbbbbbbbbbbb'
down_revision = 'aaaaaaaaaaaa'
branch_labels = None
depends_on = None


def upgrade():
    # Add created_at and updated_at columns to copilot_profiles
    # We use nullable=True first to avoid issues with existing rows, then we could set defaults if needed
    # But for simplicity in this hotfix, we leave them nullable or set server_default
    
    op.add_column('copilot_profiles', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('copilot_profiles', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Optional: Backfill existing rows with current time
    op.execute("UPDATE copilot_profiles SET created_at = NOW(), updated_at = NOW()")


def downgrade():
    op.drop_column('copilot_profiles', 'updated_at')
    op.drop_column('copilot_profiles', 'created_at')
