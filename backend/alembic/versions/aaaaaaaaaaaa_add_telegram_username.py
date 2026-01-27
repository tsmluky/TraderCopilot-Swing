"""Add telegram_username column to users table

Revision ID: aaaaaaaaaaaa
Revises: 999999999999
Create Date: 2026-01-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'aaaaaaaaaaaa'
down_revision = '999999999999'
branch_labels = None
depends_on = None


def column_exists(table_name, column_name):
    """Check if a column exists in a table (works for both SQLite and PostgreSQL)."""
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    columns = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in columns


def upgrade():
    # Add telegram_username if it doesn't exist
    if not column_exists('users', 'telegram_username'):
        op.add_column('users', sa.Column('telegram_username', sa.String(), nullable=True))


def downgrade():
    # Remove telegram_username (safe for both SQLite and PostgreSQL)
    op.drop_column('users', 'telegram_username')
