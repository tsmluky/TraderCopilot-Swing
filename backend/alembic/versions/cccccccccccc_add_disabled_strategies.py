"""Add disabled_strategies to user

Revision ID: cccccccccccc
Revises: bbbbbbbbbbbb
Create Date: 2026-02-09 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'cccccccccccc'
down_revision = 'bbbbbbbbbbbb'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    columns = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in columns

def upgrade():
    # Add disabled_strategies column to users table if not exists
    if not column_exists("users", "disabled_strategies"):
        op.add_column('users', sa.Column('disabled_strategies', sa.Text(), server_default='[]', nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('disabled_strategies')
