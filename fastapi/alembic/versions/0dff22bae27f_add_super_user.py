"""Add super user

Revision ID: 0dff22bae27f
Revises: cc177249a4f9
Create Date: 2023-10-19 17:00:10.269766

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0dff22bae27f"
down_revision: Union[str, None] = "cc177249a4f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    query = "INSERT INTO users (name,email,password,role) values ('superuser','mperez@oxyl.fr','$2b$12$81qp0AaMab2o9Ub9bKMM9emOvhanjwoPrt48d64W2GWM.JhUFavhO','super_admin');"
    op.execute(query)
    # ### end Alembic commands ###


def downgrade() -> None:
    query = "DELETE FROM users WHERE email='mperez@oxyl.fr'"
    op.execute(query)
    pass
    # ### end Alembic commands ###
