"""create creatives table

Revision ID: 004
Revises: 003
Create Date: 2025-09-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'creatives',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('idea_id', UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False, unique=True),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('firefly_job_id', sa.String(255), nullable=True),
        sa.Column('generation_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['idea_id'], ['ideas.id'], ondelete='CASCADE'),
        sa.CheckConstraint('generation_count >= 1', name='check_generation_count')
    )
    
    # Create indexes
    op.create_index('idx_creatives_idea', 'creatives', ['idea_id'], unique=False)
    op.create_index('idx_creatives_created_at', 'creatives', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_creatives_created_at')
    op.drop_index('idx_creatives_idea')
    op.drop_table('creatives')
