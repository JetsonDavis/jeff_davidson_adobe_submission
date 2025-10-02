"""
Pydantic schemas for Key entity.
"""
from pydantic import BaseModel
from typing import Dict

class KeyValuePair(BaseModel):
    """Single key-value pair"""
    key: str
    value: str

class SettingsRequest(BaseModel):
    """Request to update multiple settings"""
    settings: Dict[str, str]

class SettingsResponse(BaseModel):
    """Response with all settings"""
    settings: Dict[str, str]
