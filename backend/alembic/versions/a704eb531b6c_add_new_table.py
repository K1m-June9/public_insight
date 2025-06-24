"""add new table

Revision ID: a704eb531b6c
Revises: bb954a417306
Create Date: 2025-06-24 16:36:56.633344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a704eb531b6c'
down_revision: Union[str, None] = 'bb954a417306'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
