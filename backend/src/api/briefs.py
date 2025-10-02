"""
API endpoints for Brief management.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import json

from ..db import get_db
from ..schemas.brief import BriefCreate, BriefResponse
from ..schemas.idea import IdeaResponse
from ..services.brief_service import brief_service
from ..services.idea_service import idea_service
from ..services.creative_service import creative_service
from ..services.asset_service import asset_service
from ..services.file_handler import file_handler
from ..services.document_parser import document_parser
from ..services.llm_service import llm_service
from ..services.firefly_service import firefly_service

router = APIRouter(prefix="/briefs", tags=["briefs"])


async def _generate_missing_assets(db: Session, brief):
    """
    Generate brand logo and product images if they don't exist.
    Called automatically when a brief is created.
    """
    # Check if brand assets exist
    brand_assets = asset_service.list_assets(db, asset_type="brand")
    product_assets = asset_service.list_assets(db, asset_type="product")
    
    brand_name = brief.brand or "Brand"
    product_name = brief.product_name or "Product"
    
    # Generate brand logo if missing
    if not brand_assets:
        print(f"🎨 No brand logo found. Generating logo for '{brand_name}'...")
        try:
            logo_prompt = f"Professional minimalist logo design for brand '{brand_name}'. Clean, modern, corporate style. Simple icon or text-based logo. High contrast, suitable for marketing materials. No background, transparent or white background."
            
            # Use generate_creative which respects use_image_model setting
            file_path, mime_type, file_size, _ = await firefly_service.generate_creative(
                db=db,
                idea_content=logo_prompt,
                campaign_message="",  # No campaign message for logo
                region="US",
                demographic="General",
                aspect_ratio="1:1",
                brand_colors=None,
                language_code="en-US",
                brand_name=None,  # No brand name overlay for the logo itself
                brand_logo_path=None  # No logo compositing for logo generation
            )
            
            # Save as brand asset
            asset_service.create_asset(
                db,
                asset_type="brand",
                filename=f"{brand_name}_logo.jpg",
                file_path=file_path,
                mime_type=mime_type,
                file_size=file_size,
                auto_generated=True,
                brief_content=brief.content
            )
            print(f"✅ Generated brand logo: {file_path}")
        except Exception as e:
            print(f"⚠️  Failed to generate brand logo: {e}")
            import traceback
            print(traceback.format_exc())
    
    # Generate product image if missing
    if not product_assets:
        print(f"🎨 No product image found. Generating product image for '{product_name}'...")
        try:
            # Use brief content for better context about the product
            product_description = brief.content if brief.content else f"{product_name} product"
            product_prompt = f"Professional high-quality product photography. Product: {product_name}. Description: {product_description[:300]}. Studio lighting, clean white background, commercial advertising style. Show the product clearly with professional presentation. Make it photorealistic and appealing."
            
            # Use generate_creative which respects use_image_model setting
            file_path, mime_type, file_size, _ = await firefly_service.generate_creative(
                db=db,
                idea_content=product_prompt,
                campaign_message="",  # No campaign message for product image
                region="US",
                demographic="General",
                aspect_ratio="1:1",
                brand_colors=None,
                language_code="en-US",
                brand_name=None,  # No brand name overlay
                brand_logo_path=None  # No logo compositing
            )
            
            # Save as product asset
            asset_service.create_asset(
                db,
                asset_type="product",
                filename=f"{product_name}_image.jpg",
                file_path=file_path,
                mime_type=mime_type,
                file_size=file_size,
                auto_generated=True,
                brief_content=brief.content
            )
            print(f"✅ Generated product image: {file_path}")
        except Exception as e:
            print(f"⚠️  Failed to generate product image: {e}")
            import traceback
            print(traceback.format_exc())


@router.get("", response_model=List[BriefResponse])
def list_briefs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all briefs"""
    return brief_service.list_briefs(db, skip, limit)


@router.post("", response_model=BriefResponse, status_code=201)
async def create_brief(
    brand: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    campaign_message: str = Form(...),
    regions: str = Form(...),
    demographics: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create a new brief.
    Accepts either text content or file upload (TXT, PDF, Word).
    """
    # Parse regions and demographics from JSON strings
    try:
        regions_list = json.loads(regions)
        demographics_list = json.loads(demographics)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON for regions or demographics")
    
    # Handle file upload or text content
    source_type = "text"
    source_filename = None
    source_path = None

    if file:
        try:
            file_path, mime_type, file_size = await file_handler.save_upload(file, "briefs")
            parsed_content = await document_parser.parse_document(file_path, mime_type)

            # Try to extract brand and product name from document if not provided
            if not brand or not product_name:
                extracted_data = document_parser.extract_brand_and_product(parsed_content)
                brand = brand or extracted_data.get('brand')
                product_name = product_name or extracted_data.get('product_name')

            content = parsed_content  # Override text content with parsed
            source_type = "document"
            source_filename = file.filename
            source_path = file_path
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
    elif not content:
        raise HTTPException(status_code=400, detail="Either content or file must be provided")

    # Create brief
    brief_data = BriefCreate(
        brand=brand,
        product_name=product_name,
        content=content,
        campaign_message=campaign_message,
        regions=regions_list,
        demographics=demographics_list,
        source_type=source_type,
        source_filename=source_filename,
        source_path=source_path
    )

    # Create brief in database
    brief = brief_service.create_brief(db, brief_data)
    
    # Auto-generate brand assets if they don't exist
    await _generate_missing_assets(db, brief)
    
    return brief
@router.get("/{brief_id}", response_model=BriefResponse)
def get_brief(brief_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific brief by ID"""
    brief = brief_service.get_brief_or_404(db, brief_id)
    return brief


@router.delete("/{brief_id}", status_code=204)
def delete_brief(brief_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a brief"""
    deleted = brief_service.delete_brief(db, brief_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Brief not found")
    return None


@router.post("/{brief_id}/execute")
async def execute_brief(brief_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Execute brief to generate creative ideas with streaming updates.
    Generates one idea per region/demographic combination using LLM.
    Deletes all existing creatives in the approval queue before generating new ideas.
    Streams ideas as they are generated using Server-Sent Events.
    """
    async def generate_ideas_stream():
        try:
            # Delete all existing creatives to clear the approval queue
            all_creatives = creative_service.list_creatives(db)
            for creative in all_creatives:
                # Delete the file first
                file_handler.delete_file(creative.file_path)
                # Delete from database (cascades to approval)
                creative_service.delete_creative(db, creative.id)
            
            # Get brief
            brief = brief_service.get_brief_or_404(db, brief_id)
            
            # Send initial metadata with regions and demographics
            regions = brief.regions
            demographics = brief.demographics
            total_ideas = len(regions) * len(demographics)
            
            yield f"data: {json.dumps({'type': 'init', 'regions': regions, 'demographics': demographics, 'total': total_ideas})}\n\n"
            
            # Generate ideas one at a time and stream each
            for region in regions:
                for demographic in demographics:
                    try:
                        # Generate single idea
                        idea_data = await llm_service._generate_single_idea(
                            db,
                            brief.content,
                            brief.campaign_message,
                            region,
                            demographic,
                            *llm_service._get_provider_config(db)
                        )
                        
                        # Save to database
                        idea = idea_service.create_idea(
                            db,
                            brief_id=brief.id,
                            region=idea_data["region"],
                            demographic=idea_data["demographic"],
                            content=idea_data["content"],
                            language_code=idea_data["language_code"]
                        )
                        
                        # Stream the generated idea
                        idea_json = {
                            'type': 'idea',
                            'id': str(idea.id),
                            'brief_id': str(idea.brief_id),
                            'region': idea.region,
                            'demographic': idea.demographic,
                            'content': idea.content,
                            'language_code': idea.language_code,
                            'generation_count': idea.generation_count,
                            'created_at': idea.created_at.isoformat()
                        }
                        yield f"data: {json.dumps(idea_json)}\n\n"
                        
                    except Exception as e:
                        # Send error for this specific idea but continue
                        error_json = {
                            'type': 'error',
                            'region': region,
                            'demographic': demographic,
                            'error': str(e)
                        }
                        yield f"data: {json.dumps(error_json)}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"
            
        except Exception as e:
            # Send fatal error
            yield f"data: {json.dumps({'type': 'fatal_error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate_ideas_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
