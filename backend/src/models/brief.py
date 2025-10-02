"""
SQLAlchemy model for Brief entity.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..db import Base


class Brief(Base):
    """Brief model representing campaign briefs"""
    __tablename__ = "briefs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    campaign_message = Column(String(500), nullable=False)
    regions = Column(ARRAY(String), nullable=False)
    demographics = Column(ARRAY(String), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'text' or 'document'
    source_filename = Column(String(255), nullable=True)
    source_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ideas = relationship("Idea", back_populates="brief", cascade="all, delete-orphan")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('text', 'document', 'txt', 'pdf', 'docx')",
            name='check_source_type'
        ),
    )
    
    def __repr__(self):
        return f"<Brief(id={self.id}, source_type={self.source_type})>"
