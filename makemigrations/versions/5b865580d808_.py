"""empty message

Revision ID: 5b865580d808
Revises: f61ec7d3b08f
Create Date: 2024-02-25 00:40:33.726467

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b865580d808'
down_revision: Union[str, None] = 'f61ec7d3b08f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('tags_blog_id_fkey', 'tags', type_='foreignkey')
    op.create_foreign_key(None, 'tags', 'blogs', ['blog_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tags', type_='foreignkey')
    op.create_foreign_key('tags_blog_id_fkey', 'tags', 'blogs', ['blog_id'], ['id'])
    # ### end Alembic commands ###
