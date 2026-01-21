"""add defaults to post timestamps

Revision ID: ca02b63542f8
Revises: b70cf440ef67
Create Date: 2026-01-21 15:56:10.910915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'ca02b63542f8'
down_revision: Union[str, Sequence[str], None] = 'b70cf440ef67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("posts","created_at",server_default=sa.func.now(),)
    op.alter_column("posts","updated_at",server_default=sa.func.now(),)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("posts", "created_at", server_default=None)
    op.alter_column("posts", "updated_at", server_default=None)
