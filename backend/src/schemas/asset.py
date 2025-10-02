"""
Pydantic schemas for Asset entity.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid as uuid_pkg


class AssetResponse(BaseModel):
    """Schema for asset API responses"""
    id: uuid_pkg.UUID
    asset_type: str = Field(..., pattern="^(brand|product)$")
    filename: str
    file_path: str
    mime_type: str
    file_size: int
    brand_colors: Optional[List[str]] = None
    auto_generated: bool = False
    brief_content: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
