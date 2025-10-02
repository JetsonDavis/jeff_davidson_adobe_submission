"""
SQLAlchemy model for Idea entity.
"""
from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..db import Base


class Idea(Base):
    """
    LLM-generated creative idea for specific region/demographic combination.
    """
    __tablename__ = "ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brief_id = Column(UUID(as_uuid=True), ForeignKey('briefs.id', ondelete='CASCADE'), nullable=False)
    region = Column(String(50), nullable=False)
    demographic = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    language_code = Column(String(10), nullable=False)
    generation_count = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    brief = relationship("Brief", back_populates="ideas")
    creatives = relationship("Creative", back_populates="idea", cascade="all, delete-orphan")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            'generation_count >= 1',
            name='check_generation_count'
        ),
    )
    
    def __repr__(self):
        return f"<Idea(id={self.id}, region={self.region}, demographic={self.demographic})>"
