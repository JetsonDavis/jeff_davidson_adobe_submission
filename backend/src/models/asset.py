"""
SQLAlchemy model for Asset entity.
"""
from sqlalchemy import Column, String, Integer, TIMESTAMP, CheckConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

from ..db import Base


class Asset(Base):
    """
    Brand or product image asset.
    """
    __tablename__ = "assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_type = Column(String(10), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False, unique=True)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    brand_colors = Column(JSONB, nullable=True)
    auto_generated = Column(Boolean, default=False, nullable=False)
    brief_content = Column(String, nullable=True)  # Store brief content for regeneration
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "asset_type IN ('brand', 'product')",
            name='check_asset_type'
        ),
        CheckConstraint(
            'file_size <= 10485760',
            name='check_file_size'
        ),
    )
    
    def __repr__(self):
        return f"<Asset(id={self.id}, asset_type={self.asset_type}, filename={self.filename})>"
