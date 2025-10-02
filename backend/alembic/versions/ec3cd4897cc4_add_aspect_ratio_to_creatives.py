"""add_aspect_ratio_to_creatives

Revision ID: ec3cd4897cc4
Revises: 005
Create Date: 2025-09-30 18:55:08.096368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec3cd4897cc4'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('creatives', sa.Column('aspect_ratio', sa.String(10), nullable=False, server_default='1:1'))


def downgrade() -> None:
    op.drop_column('creatives', 'aspect_ratio')
