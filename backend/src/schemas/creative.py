"""
Pydantic schemas for Creative entity.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

from .approval import ApprovalResponse


class CreativeResponse(BaseModel):
    """Response schema for Creative"""
    id: uuid.UUID
    idea_id: uuid.UUID
    file_path: str
    mime_type: str
    file_size: int
    firefly_job_id: Optional[str]
    aspect_ratio: str
    generation_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreativeWithApproval(CreativeResponse):
    """Schema for creative with approval status"""
    approval: ApprovalResponse
    region: Optional[str] = None
    demographic: Optional[str] = None
    brand: Optional[str] = None
    product_name: Optional[str] = None

    class Config:
        from_attributes = True
