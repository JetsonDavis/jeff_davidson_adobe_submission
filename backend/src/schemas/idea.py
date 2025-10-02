"""
Pydantic schemas for Idea entity.
"""
from pydantic import BaseModel, Field
from datetime import datetime
import uuid as uuid_pkg


class IdeaResponse(BaseModel):
    """Schema for idea API responses"""
    id: uuid_pkg.UUID
    brief_id: uuid_pkg.UUID
    region: str
    demographic: str
    content: str
    language_code: str
    generation_count: int = Field(..., ge=1)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
