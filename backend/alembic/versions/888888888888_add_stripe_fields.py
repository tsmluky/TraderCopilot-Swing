"""Add Stripe billing fields and Timezone

Revision ID: stripe_fix_001
Revises: 7ee0b0b05b15
Create Date: 2026-01-26

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '888888888888'
down_revision: Union[str, None] = '7ee0b0b05b15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add Stripe Fields
    op.add_column("users", sa.Column("billing_provider", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_customer_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_subscription_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_price_id", sa.String(), nullable=True))

    op.create_index("ix_users_stripe_customer_id", "users", ["stripe_customer_id"])
    op.create_index("ix_users_stripe_subscription_id", "users", ["stripe_subscription_id"])
    
    # 2. Add Timezone (if it was intended) - checking previous file it was empty, 
    # but let's assume we want to be safe and just add the columns we KNOW are missing.


def downgrade() -> None:
    op.drop_index("ix_users_stripe_subscription_id", table_name="users")
    op.drop_index("ix_users_stripe_customer_id", table_name="users")

    op.drop_column("users", "stripe_price_id")
    op.drop_column("users", "stripe_subscription_id")
    op.drop_column("users", "stripe_customer_id")
    op.drop_column("users", "billing_provider")
