"""add stripe fields

Revision ID: manual_stripe_01
Revises: 
Create Date: 2026-01-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'manual_stripe_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Helper to check if column exists to avoid errors in messy envs
    # In pure Alembic usually we just assume, but for safety:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    columns = [c['name'] for c in insp.get_columns('users')]

    if 'billing_provider' not in columns:
        op.add_column('users', sa.Column('billing_provider', sa.String(), nullable=True))
    
    if 'stripe_customer_id' not in columns:
        op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))
        op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=False)
    
    if 'stripe_subscription_id' not in columns:
        op.add_column('users', sa.Column('stripe_subscription_id', sa.String(), nullable=True))
        op.create_index(op.f('ix_users_stripe_subscription_id'), 'users', ['stripe_subscription_id'], unique=False)

    if 'stripe_price_id' not in columns:
        op.add_column('users', sa.Column('stripe_price_id', sa.String(), nullable=True))

    if 'plan_status' not in columns:
        op.add_column('users', sa.Column('plan_status', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'plan_status')
    op.drop_column('users', 'stripe_price_id')
    op.drop_index(op.f('ix_users_stripe_subscription_id'), table_name='users')
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_index(op.f('ix_users_stripe_customer_id'), table_name='users')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'billing_provider')
