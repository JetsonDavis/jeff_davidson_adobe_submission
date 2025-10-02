"""
API endpoints for Asset management.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from ..db import get_db
from ..schemas.asset import AssetResponse
from ..services.asset_service import asset_service
from ..services.file_handler import file_handler
from ..services.color_extractor import color_extractor
from ..services.firefly_service import firefly_service

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("/brand", response_model=AssetResponse, status_code=201)
async def upload_brand_asset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload brand asset (logo, brand imagery) - JPG or PNG"""
    # Save file
    file_path, original_filename, file_size = await file_handler.save_brand_asset(file)
    
    # Extract brand colors
    try:
        brand_colors = color_extractor.extract_colors(file_path, num_colors=5)
    except Exception as e:
        print(f"Warning: Could not extract colors: {e}")
        brand_colors = None
    
    # Create asset in database
    asset = asset_service.create_asset(
        db,
        asset_type="brand",
        filename=original_filename,
        file_path=file_path,
        mime_type=file.content_type,
        file_size=file_size,
        brand_colors=brand_colors
    )
    
    return asset


@router.post("/product", response_model=AssetResponse, status_code=201)
async def upload_product_asset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload product asset (product imagery) - JPG or PNG"""
    # Save file
    file_path, original_filename, file_size = await file_handler.save_product_asset(file)
    
    # Create asset in database
    asset = asset_service.create_asset(
        db,
        asset_type="product",
        filename=original_filename,
        file_path=file_path,
        mime_type=file.content_type,
        file_size=file_size
    )
    
    return asset


@router.get("", response_model=List[AssetResponse])
def list_assets(
    asset_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all assets with optional filtering by type (brand/product)"""
    assets = asset_service.list_assets(db, asset_type=asset_type, skip=skip, limit=limit)
    return assets


@router.post("/{asset_id}/regenerate", response_model=AssetResponse)
async def regenerate_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Regenerate an auto-generated asset with new AI-generated image"""
    # Get existing asset
    asset = asset_service.get_asset_or_404(db, asset_id)
    
    if not asset.auto_generated:
        raise HTTPException(status_code=400, detail="Can only regenerate auto-generated assets")
    
    # Extract brand and product name from filename
    parts = asset.filename.rsplit('_', 1)
    name = parts[0] if len(parts) > 0 else "Asset"
    
    # Generate new image based on asset type
    try:
        if asset.asset_type == "brand":
            prompt = f"Professional minimalist logo design for brand '{name}'. Clean, modern, corporate style. Simple icon or text-based logo. High contrast, suitable for marketing materials. No background, transparent or white background."
        else:  # product
            product_description = asset.brief_content if asset.brief_content else f"{name} product"
            prompt = f"Professional high-quality product photography. Product: {name}. Description: {product_description[:300]}. Studio lighting, clean white background, commercial advertising style. Show the product clearly with professional presentation. Make it photorealistic and appealing."
        
        file_path, mime_type, file_size, _ = await firefly_service._call_firefly_api(
            prompt=prompt,
            aspect_ratio="1:1",
            api_key=firefly_service._get_provider_config(db)[0],
            api_url=firefly_service._get_provider_config(db)[1],
            provider=firefly_service._get_provider_config(db)[2],
            db=db
        )
        
        # Delete old file
        file_handler.delete_file(asset.file_path)
        
        # Update asset with new file
        asset.file_path = file_path
        asset.mime_type = mime_type
        asset.file_size = file_size
        db.commit()
        db.refresh(asset)
        
        print(f"✅ Regenerated {asset.asset_type} asset: {file_path}")
        return asset
        
    except Exception as e:
        print(f"❌ Failed to regenerate asset: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate asset: {str(e)}")


@router.delete("/{asset_id}", status_code=204)
def delete_asset(asset_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete an asset"""
    # Get asset to get file path
    asset = asset_service.get_asset_or_404(db, asset_id)
    
    # Delete from filesystem
    file_handler.delete_file(asset.file_path)
    
    # Delete from database
    asset_service.delete_asset(db, asset_id)
    
    return None
