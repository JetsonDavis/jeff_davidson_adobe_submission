"""
SQLAlchemy model for Approval entity.
"""
from sqlalchemy import Column, Boolean, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..db import Base


class Approval(Base):
    """
    Approval workflow tracking for creatives.
    Requires both creative and regional approval before deployment.
    """
    __tablename__ = "approvals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creative_id = Column(UUID(as_uuid=True), ForeignKey('creatives.id', ondelete='CASCADE'), nullable=False, unique=True)
    creative_approved = Column(Boolean, nullable=False, default=False)
    creative_approved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    regional_approved = Column(Boolean, nullable=False, default=False)
    regional_approved_at = Column(TIMESTAMP(timezone=True), nullable=True)
    deployed = Column(Boolean, nullable=False, default=False)
    deployed_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creative = relationship("Creative", back_populates="approval")
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "deployed = false OR (creative_approved = true AND regional_approved = true)",
            name='check_deployed_requires_approvals'
        ),
    )
    
    def __repr__(self):
        return f"<Approval(id={self.id}, creative_approved={self.creative_approved}, regional_approved={self.regional_approved}, deployed={self.deployed})>"
