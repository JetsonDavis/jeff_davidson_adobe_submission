"""
Pydantic schemas for Approval entity.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid as uuid_pkg


class ApprovalResponse(BaseModel):
    """Schema for approval API responses"""
    id: uuid_pkg.UUID
    creative_id: uuid_pkg.UUID
    creative_approved: bool
    creative_approved_at: Optional[datetime] = None
    regional_approved: bool
    regional_approved_at: Optional[datetime] = None
    deployed: bool
    deployed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
