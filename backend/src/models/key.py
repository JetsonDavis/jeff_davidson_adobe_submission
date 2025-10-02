"""
SQLAlchemy model for Key entity (settings storage).
"""
from sqlalchemy import Column, String, DateTime
from datetime import datetime

from ..db import Base


class Key(Base):
    """Key-value store for application settings"""
    __tablename__ = "keys"
    
    key = Column(String, primary_key=True, nullable=False)
    value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
