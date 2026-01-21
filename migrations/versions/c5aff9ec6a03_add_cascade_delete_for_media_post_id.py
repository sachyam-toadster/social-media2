"""Add cascade delete for media.post_id

Revision ID: c5aff9ec6a03
Revises: ca02b63542f8
Create Date: 2026-01-21 16:24:08.216132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c5aff9ec6a03'
down_revision: Union[str, Sequence[str], None] = 'ca02b63542f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(op.f('media_post_id_fkey'),'media',type_='foreignkey')

    op.create_foreign_key('media_post_id_fkey','media','posts',['post_id'],['id'],ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_constraint('media_post_id_fkey','media',type_='foreignkey')
    op.create_foreign_key('media_post_id_fkey','media','posts',['post_id'],['id'])