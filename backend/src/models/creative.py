"""
SQLAlchemy model for Creative entity.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..db import Base


class Creative(Base):
    """Creative entity - generated social media content"""
    __tablename__ = "creatives"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    firefly_job_id = Column(String, nullable=True)
    aspect_ratio = Column(String(10), nullable=False, default="1:1")
    generation_count = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    idea = relationship("Idea", back_populates="creatives")
    approval = relationship("Approval", back_populates="creative", uselist=False, cascade="all, delete-orphan")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            'generation_count >= 1',
            name='check_generation_count'
        ),
    )
    
    def __repr__(self):
        return f"<Creative(id={self.id}, idea_id={self.idea_id})>"
