"""
CRUD service for Asset entity.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import uuid

from ..models.asset import Asset


class AssetService:
    """Handles CRUD operations for assets"""
    
    def create_asset(
        self,
        db: Session,
        asset_type: str,
        filename: str,
        file_path: str,
        mime_type: str,
        file_size: int,
        brand_colors: Optional[List[str]] = None,
        auto_generated: bool = False,
        brief_content: Optional[str] = None
    ) -> Asset:
        """
        Create a new asset.
        
        Args:
            db: Database session
            asset_type: Type of asset ('brand' or 'product')
            filename: Original filename
            file_path: Filesystem path
            mime_type: MIME type
            file_size: File size in bytes
            brand_colors: Optional list of brand colors (for brand assets)
            auto_generated: Whether this asset was auto-generated
            brief_content: Brief content for regeneration reference
        
        Returns:
            Created Asset instance
        """
        asset = Asset(
            asset_type=asset_type,
            filename=filename,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            brand_colors=brand_colors,
            auto_generated=auto_generated,
            brief_content=brief_content
        )
        
        db.add(asset)
        db.commit()
        db.refresh(asset)
        
        return asset
    
    def get_asset(self, db: Session, asset_id: uuid.UUID) -> Optional[Asset]:
        """Get asset by ID"""
        return db.query(Asset).filter(Asset.id == asset_id).first()
    
    def get_asset_or_404(self, db: Session, asset_id: uuid.UUID) -> Asset:
        """Get asset by ID or raise 404"""
        asset = self.get_asset(db, asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    
    def list_assets(
        self,
        db: Session,
        asset_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Asset]:
        """
        List assets with optional filtering by type.
        
        Args:
            db: Database session
            asset_type: Optional filter by 'brand' or 'product'
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Asset instances
        """
        query = db.query(Asset)
        
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        
        return query.order_by(Asset.created_at.desc()).offset(skip).limit(limit).all()
    
    def delete_asset(self, db: Session, asset_id: uuid.UUID) -> bool:
        """Delete asset by ID"""
        asset = self.get_asset(db, asset_id)
        if not asset:
            return False
        
        db.delete(asset)
        db.commit()
        return True


# Singleton instance
asset_service = AssetService()
