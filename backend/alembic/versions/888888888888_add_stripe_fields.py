"""Add Stripe billing fields and Timezone

Revision ID: 888888888888
Revises: 7ee0b0b05b15
Create Date: 2026-01-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '888888888888'
down_revision: Union[str, None] = '7ee0b0b05b15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name, column_name):
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    columns = [c['name'] for c in insp.get_columns(table_name)]
    return column_name in columns

def index_exists(table_name, index_name):
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    indexes = [c['name'] for c in insp.get_indexes(table_name)]
    return index_name in indexes

def upgrade() -> None:
    # 1. Add Stripe Fields if not exist
    if not column_exists("users", "billing_provider"):
        op.add_column("users", sa.Column("billing_provider", sa.String(), nullable=True))
    
    if not column_exists("users", "stripe_customer_id"):
        op.add_column("users", sa.Column("stripe_customer_id", sa.String(), nullable=True))
    
    if not column_exists("users", "stripe_subscription_id"):
        op.add_column("users", sa.Column("stripe_subscription_id", sa.String(), nullable=True))
        
    if not column_exists("users", "stripe_price_id"):
        op.add_column("users", sa.Column("stripe_price_id", sa.String(), nullable=True))

    # 2. Add Indexes if not exist
    if not index_exists("users", "ix_users_stripe_customer_id"):
        op.create_index("ix_users_stripe_customer_id", "users", ["stripe_customer_id"])
        
    if not index_exists("users", "ix_users_stripe_subscription_id"):
        op.create_index("ix_users_stripe_subscription_id", "users", ["stripe_subscription_id"])


def downgrade() -> None:
    op.drop_index("ix_users_stripe_subscription_id", table_name="users")
    op.drop_index("ix_users_stripe_customer_id", table_name="users")

    op.drop_column("users", "stripe_price_id")
    op.drop_column("users", "stripe_subscription_id")
    op.drop_column("users", "stripe_customer_id")
    op.drop_column("users", "billing_provider")
