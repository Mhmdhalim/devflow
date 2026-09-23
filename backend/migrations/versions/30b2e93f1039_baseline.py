"""baseline

Revision ID: 30b2e93f1039
Revises: cc4ae3e2ee8c
Create Date: 2026-09-23 16:57:23.792584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30b2e93f1039'
down_revision: Union[str, Sequence[str], None] = 'cc4ae3e2ee8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
