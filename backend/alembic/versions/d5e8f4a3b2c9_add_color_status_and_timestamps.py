"""Add color status and timestamps

Revision ID: d5e8f4a3b2c9
Revises: c8f9d3e2a1b5
Create Date: 2025-10-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5e8f4a3b2c9'
down_revision: Union[str, Sequence[str], None] = 'c8f9d3e2a1b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column to colors table
    op.add_column('colors', sa.Column('status', sa.String(), nullable=False, server_default='active'))

    # Add timestamps to fabric_families
    op.add_column('fabric_families', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('fabric_families', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()))

    # Add timestamps to colors
    op.add_column('colors', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('colors', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()))

    # Create indexes for better query performance
    op.create_index('ix_colors_status', 'colors', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_colors_status', table_name='colors')

    # Drop timestamp columns from colors
    op.drop_column('colors', 'updated_at')
    op.drop_column('colors', 'created_at')

    # Drop timestamp columns from fabric_families
    op.drop_column('fabric_families', 'updated_at')
    op.drop_column('fabric_families', 'created_at')

    # Drop status column from colors
    op.drop_column('colors', 'status')
