"""Add swatch_code to colors

Revision ID: c8f9d3e2a1b5
Revises: ad4ff826127b
Create Date: 2025-10-29 23:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f9d3e2a1b5'
down_revision: Union[str, Sequence[str], None] = 'ad4ff826127b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add swatch_code column to colors table
    op.add_column('colors', sa.Column('swatch_code', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove swatch_code column from colors table
    op.drop_column('colors', 'swatch_code')
