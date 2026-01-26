"""Add Stripe billing fields to users

Revision ID: a19c2f3b7c11
Revises: d32f6e15bf54
Create Date: 2026-01-24

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a19c2f3b7c11'
down_revision = 'd32f6e15bf54'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("billing_provider", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_customer_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_subscription_id", sa.String(), nullable=True))
    op.add_column("users", sa.Column("stripe_price_id", sa.String(), nullable=True))

    op.create_index("ix_users_stripe_customer_id", "users", ["stripe_customer_id"])
    op.create_index("ix_users_stripe_subscription_id", "users", ["stripe_subscription_id"])


def downgrade() -> None:
    op.drop_index("ix_users_stripe_subscription_id", table_name="users")
    op.drop_index("ix_users_stripe_customer_id", table_name="users")

    op.drop_column("users", "stripe_price_id")
    op.drop_column("users", "stripe_subscription_id")
    op.drop_column("users", "stripe_customer_id")
    op.drop_column("users", "billing_provider")
