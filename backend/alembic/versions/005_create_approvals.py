"""create approvals table

Revision ID: 005
Revises: 004
Create Date: 2025-09-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'approvals',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('creative_id', UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('creative_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creative_approved_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('regional_approved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('regional_approved_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('deployed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deployed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['creative_id'], ['creatives.id'], ondelete='CASCADE'),
        sa.CheckConstraint(
            "deployed = false OR (creative_approved = true AND regional_approved = true)",
            name='check_deployed_requires_approvals'
        )
    )
    
    # Create indexes
    op.create_index('idx_approvals_creative', 'approvals', ['creative_id'], unique=False)
    op.create_index(
        'idx_approvals_status',
        'approvals',
        ['creative_approved', 'regional_approved', 'deployed'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_approvals_status')
    op.drop_index('idx_approvals_creative')
    op.drop_table('approvals')
