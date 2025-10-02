"""
API endpoints for Settings management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas.key import SettingsRequest, SettingsResponse
from ..services.key_service import key_service

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Get all settings"""
    settings = key_service.get_all(db)
    return {"settings": settings}


@router.post("", response_model=SettingsResponse)
def update_settings(request: SettingsRequest, db: Session = Depends(get_db)):
    """Update multiple settings"""
    settings = key_service.set_multiple(db, request.settings)
    return {"settings": settings}
