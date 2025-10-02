"""
API endpoints for Creative management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..db import get_db
from ..schemas.creative import CreativeResponse, CreativeWithApproval
from ..services.creative_service import creative_service
from ..services.idea_service import idea_service
from ..services.brief_service import brief_service
from ..services.asset_service import asset_service
from ..services.firefly_service import firefly_service
from ..services.file_handler import file_handler

router = APIRouter(prefix="/creatives", tags=["creatives"])


@router.get("", response_model=List[CreativeWithApproval])
def list_creatives(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all creatives with approval status.
    Filter by status: pending, approved, deployed
    """
    creatives = creative_service.list_creatives(db, status=status, skip=skip, limit=limit)
    # Add region, demographic from idea and brand, product_name from brief
    result = []
    for creative in creatives:
        creative_dict = CreativeWithApproval.model_validate(creative).model_dump(mode='json')
        if creative.idea:
            creative_dict['region'] = creative.idea.region
            creative_dict['demographic'] = creative.idea.demographic
            # Get brief information through idea
            if creative.idea.brief:
                creative_dict['brand'] = creative.idea.brief.brand
                creative_dict['product_name'] = creative.idea.brief.product_name
        result.append(creative_dict)
    return result


@router.get("/{creative_id}", response_model=CreativeWithApproval)
def get_creative(creative_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific creative by ID with approval status"""
    creative = creative_service.get_creative_or_404(db, creative_id)
    return creative


@router.post("/{creative_id}/regenerate", response_model=CreativeResponse)
async def regenerate_creative(creative_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Regenerate creative with new Firefly-generated image.
    Resets all approvals to false - must re-approve before deploying.
    """
    # Get creative and idea
    creative = creative_service.get_creative_or_404(db, creative_id)
    idea = idea_service.get_idea_or_404(db, creative.idea_id)
    brief = brief_service.get_brief_or_404(db, idea.brief_id)
    
    # Get brand colors and logo
    brand_assets = asset_service.list_assets(db, asset_type="brand")
    brand_colors = brand_assets[0].brand_colors if brand_assets else None
    brand_logo_path = brand_assets[0].file_path if brand_assets else None
    
    # Generate new creative
    try:
        new_file_path, mime_type, new_file_size, firefly_job_id = await firefly_service.generate_creative(
            db,
            idea.content,
            brief.campaign_message,
            idea.region,
            idea.demographic,
            creative.aspect_ratio,
            brand_colors,
            idea.language_code,
            brief.brand,
            brand_logo_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firefly generation failed: {str(e)}")
    
    # Delete old file
    file_handler.delete_file(creative.file_path)
    
    # Update creative in database (resets approvals)
    updated_creative = creative_service.regenerate_creative(
        db,
        creative_id,
        new_file_path,
        new_file_size,
        firefly_job_id
    )
    
    return updated_creative


@router.delete("/{creative_id}", status_code=204)
def delete_creative(creative_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a single creative by ID."""
    creative = creative_service.get_creative_or_404(db, creative_id)
    file_handler.delete_file(creative.file_path)
    creative_service.delete_creative(db, creative_id)
    return None


@router.delete("/by-idea/{idea_id}", status_code=204)
def delete_creatives_by_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Delete all creatives associated with a specific idea.
    This removes all aspect ratios for the given idea.
    """
    from ..models.creative import Creative
    
    # Get all creatives for this idea
    creatives = db.query(Creative).filter(Creative.idea_id == idea_id).all()
    
    if not creatives:
        raise HTTPException(status_code=404, detail="No creatives found for this idea")
    
    # Delete files and database records
    for creative in creatives:
        file_handler.delete_file(creative.file_path)
        creative_service.delete_creative(db, creative.id)
    
    return None
