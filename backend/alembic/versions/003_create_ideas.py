"""create ideas table

Revision ID: 003
Revises: 002
Create Date: 2025-09-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ideas',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('brief_id', UUID(as_uuid=True), nullable=False),
        sa.Column('region', sa.String(50), nullable=False),
        sa.Column('demographic', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language_code', sa.String(10), nullable=False),
        sa.Column('generation_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['brief_id'], ['briefs.id'], ondelete='CASCADE'),
        sa.CheckConstraint('generation_count >= 1', name='check_generation_count')
    )
    
    # Create indexes
    op.create_index('idx_ideas_brief', 'ideas', ['brief_id'], unique=False)
    op.create_index('idx_ideas_created_at', 'ideas', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_ideas_created_at')
    op.drop_index('idx_ideas_brief')
    op.drop_table('ideas')
