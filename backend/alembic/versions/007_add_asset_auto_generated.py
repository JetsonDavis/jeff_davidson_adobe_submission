"""add asset auto_generated and brief_content

Revision ID: 007
Revises: 006
Create Date: 2025-10-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add auto_generated column with default False
    op.add_column('assets', sa.Column('auto_generated', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add brief_content column
    op.add_column('assets', sa.Column('brief_content', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the columns
    op.drop_column('assets', 'brief_content')
    op.drop_column('assets', 'auto_generated')
