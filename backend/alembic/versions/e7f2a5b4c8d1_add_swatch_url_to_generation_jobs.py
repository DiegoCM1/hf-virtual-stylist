"""Add swatch_url to generation_jobs

Revision ID: e7f2a5b4c8d1
Revises: d5e8f4a3b2c9
Create Date: 2025-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f2a5b4c8d1'
down_revision: Union[str, Sequence[str], None] = 'd5e8f4a3b2c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add swatch_url column to generation_jobs table
    op.add_column('generation_jobs', sa.Column('swatch_url', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove swatch_url column from generation_jobs table
    op.drop_column('generation_jobs', 'swatch_url')
