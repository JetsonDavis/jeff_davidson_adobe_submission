"""
Pydantic schemas for Brief entity.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import uuid as uuid_pkg

if TYPE_CHECKING:
    from .idea import IdeaResponse


class BriefCreate(BaseModel):
    """Schema for creating a new brief"""
    brand: Optional[str] = Field(None, max_length=255, description="Brand name")
    product_name: Optional[str] = Field(None, max_length=255, description="Product name")
    content: str = Field(..., min_length=1, description="Product brief text")
    campaign_message: str = Field(..., min_length=1, max_length=500)
    regions: List[str] = Field(..., min_items=1)
    demographics: List[str] = Field(..., min_items=1)
    source_type: str = Field(..., pattern="^(text|document)$")
    source_filename: Optional[str] = None
    source_path: Optional[str] = None


class BriefResponse(BaseModel):
    """Response schema for Brief"""
    id: uuid_pkg.UUID
    brand: Optional[str] = None
    product_name: Optional[str] = None
    content: str
    campaign_message: str
    regions: List[str]
    demographics: List[str]
    source_type: str
    source_filename: Optional[str]
    source_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    ideas: List['IdeaResponse'] = []
    
    class Config:
        from_attributes = True


# Resolve forward references
from .idea import IdeaResponse
BriefResponse.model_rebuild()
