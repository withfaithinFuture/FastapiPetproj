"""add_age

Revision ID: de3dd0bd8c29
Revises: f568e543e854
Create Date: 2026-01-26 00:54:51.251289
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'de3dd0bd8c29'
down_revision: Union[str, Sequence[str], None] = 'f568e543e854'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('age', sa.String(), nullable=False))

def downgrade() -> None:
    op.drop_column('users', 'age')