"""baseline

Revision ID: cc4ae3e2ee8c
Revises:
Create Date: 2026-09-23 16:51:08.024276

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "cc4ae3e2ee8c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
