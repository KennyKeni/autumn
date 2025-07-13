"""create partition table

Revision ID: 40839b751170
Revises: 54a7ddabe5e2
Create Date: 2025-07-13 10:16:36.919679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40839b751170'
down_revision: Union[str, Sequence[str], None] = '54a7ddabe5e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
