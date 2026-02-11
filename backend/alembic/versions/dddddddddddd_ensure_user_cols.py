
"""Ensure user columns role and name

Revision ID: dddddddddddd
Revises: cccccccccccc
Create Date: 2026-02-11 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'ddddddddddddd'
down_revision = 'cccccccccccc'
branch_labels = None
depends_on = None

def column_exists(table_name, column_name):
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    columns = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in columns

def upgrade():
    # 1. Ensure 'role' column exists
    if not column_exists("users", "role"):
        print("Adding 'role' column to users table...")
        op.add_column("users", sa.Column("role", sa.String(), server_default="user"))
    
    # 2. Ensure 'name' column exists
    if not column_exists("users", "name"):
        print("Adding 'name' column to users table...")
        op.add_column("users", sa.Column("name", sa.String(), nullable=True))

def downgrade():
    # We generally don't want to drop 'role' and 'name' if they contain data
    # But for strict downgrade:
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("role")
        batch_op.drop_column("name")
