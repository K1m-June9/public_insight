"""empty message

Revision ID: b816aaaafe10
Revises: a704eb531b6c
Create Date: 2025-06-24 16:39:06.816658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b816aaaafe10'
down_revision: Union[str, None] = 'a704eb531b6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
