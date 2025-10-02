"""create briefs table

Revision ID: 001
Revises: 
Create Date: 2025-09-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create briefs table
    op.create_table(
        'briefs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('campaign_message', sa.Text(), nullable=False),
        sa.Column('regions', JSONB, nullable=False),
        sa.Column('demographics', JSONB, nullable=False),
        sa.Column('source_type', sa.String(10), nullable=False),
        sa.Column('source_filename', sa.String(255), nullable=True),
        sa.Column('source_path', sa.String(512), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("source_type IN ('text', 'txt', 'pdf', 'docx')", name='check_source_type')
    )
    
    # Create index
    op.create_index('idx_briefs_created_at', 'briefs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_briefs_created_at')
    op.drop_table('briefs')
