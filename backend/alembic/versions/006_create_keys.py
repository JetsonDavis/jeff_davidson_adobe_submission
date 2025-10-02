"""create keys table

Revision ID: 006
Revises: 005
Create Date: 2025-09-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = 'ec3cd4897cc4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'keys',
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('key')
    )


def downgrade() -> None:
    op.drop_table('keys')
