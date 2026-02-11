"""Add telegram_chat_id to user

Revision ID: 7ee0b0b05b15
Revises:
Create Date: 2025-12-30 20:45:55.510221

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = "7ee0b0b05b15"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_context().bind
    insp = Inspector.from_engine(bind)
    indexes = [idx['name'] for idx in insp.get_indexes('signals')]
    
    if "ix_signals_idempotency_key" not in indexes:
        op.create_index(
            op.f("ix_signals_idempotency_key"), "signals", ["idempotency_key"], unique=True
        )
    else:
        print("Index ix_signals_idempotency_key already exists. Skipping.")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_signals_idempotency_key"), table_name="signals")
