"""Add cascade delete for comments.post_id

Revision ID: 60b6b043417b
Revises: c5aff9ec6a03
Create Date: 2026-01-21 16:46:38.098762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '60b6b043417b'
down_revision: Union[str, Sequence[str], None] = 'c5aff9ec6a03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        op.f('comments_post_id_fkey'),
        'comments',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'comments_post_id_fkey',
        'comments',
        'posts',
        ['post_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint(
        'comments_post_id_fkey',
        'comments',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'comments_post_id_fkey',
        'comments',
        'posts',
        ['post_id'],
        ['id']
    )
