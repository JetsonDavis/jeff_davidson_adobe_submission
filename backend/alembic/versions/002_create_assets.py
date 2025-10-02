"""create assets table

Revision ID: 002
Revises: 001
Create Date: 2025-09-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'assets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('asset_type', sa.String(10), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False, unique=True),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('brand_colors', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint("asset_type IN ('brand', 'product')", name='check_asset_type'),
        sa.CheckConstraint('file_size <= 10485760', name='check_file_size')
    )
    
    # Create indexes
    op.create_index('idx_assets_type', 'assets', ['asset_type'], unique=False)
    op.create_index('idx_assets_created_at', 'assets', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_assets_created_at')
    op.drop_index('idx_assets_type')
    op.drop_table('assets')
