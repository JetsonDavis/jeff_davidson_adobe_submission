"""
API endpoints for Idea management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from ..db import get_db
from ..schemas.idea import IdeaResponse
from ..schemas.creative import CreativeResponse
from ..services.idea_service import idea_service
from ..services.creative_service import creative_service
from ..services.brief_service import brief_service
from ..services.asset_service import asset_service
from ..services.llm_service import llm_service
from ..services.firefly_service import firefly_service

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.get("/{idea_id}", response_model=IdeaResponse)
def get_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific idea by ID"""
    idea = idea_service.get_idea_or_404(db, idea_id)
    return idea


@router.post("/{idea_id}/regenerate", response_model=IdeaResponse)
async def regenerate_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Regenerate an idea with new LLM-generated content.
    Preserves region, demographic, and brief association.
    """
    # Get existing idea
    idea = idea_service.get_idea_or_404(db, idea_id)
    
    # Get parent brief for context
    brief = brief_service.get_brief_or_404(db, idea.brief_id)
    
    # Generate new idea content
    try:
        idea_data_list = await llm_service.generate_ideas(
            db,
            brief.content,
            brief.campaign_message,
            [idea.region],
            [idea.demographic]
        )
        new_content = idea_data_list[0]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    
    # Update idea with new content
    updated_idea = idea_service.regenerate_idea(db, idea_id, new_content)
    
    return updated_idea


@router.post("/{idea_id}/generate-creative", response_model=list[CreativeResponse], status_code=201)
async def generate_creative(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Generate final creative assets from idea using Adobe Firefly.
    Creates 3 versions: 16:9, 9:16, and 1:1 aspect ratios.
    Includes campaign message and brand colors in the generated images.
    """
    # Get idea and brief
    idea = idea_service.get_idea_or_404(db, idea_id)
    brief = brief_service.get_brief_or_404(db, idea.brief_id)
    
    # Get brand colors and logo from assets (if any)
    brand_assets = asset_service.list_assets(db, asset_type="brand")
    brand_colors = None
    brand_logo_path = None
    if brand_assets:
        # Use colors and logo from first brand asset
        brand_colors = brand_assets[0].brand_colors
        brand_logo_path = brand_assets[0].file_path
    
    # Generate creatives for all 3 aspect ratios
    aspect_ratios = ["16:9", "9:16", "1:1"]
    creatives = []
    
    for aspect_ratio in aspect_ratios:
        try:
            file_path, mime_type, file_size, firefly_job_id = await firefly_service.generate_creative(
                db,
                idea.content,
                brief.campaign_message,
                idea.region,
                idea.demographic,
                aspect_ratio,
                brand_colors,
                idea.language_code,  # Pass language for appropriate text
                brief.brand,  # Pass brand name for logo generation
                brand_logo_path  # Pass brand logo path for compositing
            )
        except Exception as e:
            import traceback
            error_details = f"Firefly generation failed for {aspect_ratio}: {str(e)}\n{traceback.format_exc()}"
            print(error_details)  # Log to console
            raise HTTPException(status_code=500, detail=error_details)
        
        # Create creative in database (also creates approval record)
        creative = creative_service.create_creative(
            db,
            idea_id=idea.id,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            aspect_ratio=aspect_ratio,
            firefly_job_id=firefly_job_id
        )
        creatives.append(creative)
    
    return creatives


@router.post("/{idea_id}/duplicate", response_model=IdeaResponse, status_code=201)
def duplicate_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Duplicate an idea with the same region, demographic, and content.
    This creates a new idea that can have its own set of creatives.
    """
    # Get existing idea
    idea = idea_service.get_idea_or_404(db, idea_id)
    
    # Create duplicate idea
    duplicate = idea_service.create_idea(
        db,
        brief_id=idea.brief_id,
        region=idea.region,
        demographic=idea.demographic,
        content=idea.content,
        language_code=idea.language_code
    )
    
    return duplicate


@router.delete("/{idea_id}", status_code=204)
def delete_idea(idea_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete an idea and its associated creatives"""
    idea_service.delete_idea(db, idea_id)
    return None
