"""
CRUD service for Brief entity.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import uuid

from ..models.brief import Brief
from ..schemas.brief import BriefCreate, BriefResponse


class BriefService:
    """Handles CRUD operations for briefs"""
    
    def create_brief(self, db: Session, brief_data: BriefCreate) -> Brief:
        """
        Create a new brief.
        
        Args:
            db: Database session
            brief_data: Brief creation data
        
        Returns:
            Created Brief instance
        """
        brief = Brief(
            brand=brief_data.brand,
            product_name=brief_data.product_name,
            content=brief_data.content,
            campaign_message=brief_data.campaign_message,
            regions=brief_data.regions,
            demographics=brief_data.demographics,
            source_type=brief_data.source_type,
            source_filename=brief_data.source_filename,
            source_path=brief_data.source_path
        )
        
        db.add(brief)
        db.commit()
        db.refresh(brief)
        
        return brief
    
    def get_brief(self, db: Session, brief_id: uuid.UUID) -> Optional[Brief]:
        """
        Get brief by ID.
        
        Args:
            db: Database session
            brief_id: Brief UUID
        
        Returns:
            Brief instance or None
        """
        return db.query(Brief).filter(Brief.id == brief_id).first()
    
    def get_brief_or_404(self, db: Session, brief_id: uuid.UUID) -> Brief:
        """
        Get brief by ID or raise 404.
        
        Args:
            db: Database session
            brief_id: Brief UUID
        
        Returns:
            Brief instance
        
        Raises:
            HTTPException: 404 if not found
        """
        brief = self.get_brief(db, brief_id)
        if not brief:
            raise HTTPException(status_code=404, detail="Brief not found")
        return brief
    
    def list_briefs(self, db: Session, skip: int = 0, limit: int = 100) -> List[Brief]:
        """
        List all briefs with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Brief instances
        """
        return db.query(Brief).order_by(Brief.created_at.desc()).offset(skip).limit(limit).all()
    
    def delete_brief(self, db: Session, brief_id: uuid.UUID) -> bool:
        """
        Delete brief by ID.
        
        Args:
            db: Database session
            brief_id: Brief UUID
        
        Returns:
            True if deleted, False if not found
        """
        brief = self.get_brief(db, brief_id)
        if not brief:
            return False
        
        db.delete(brief)
        db.commit()
        return True


# Singleton instance
brief_service = BriefService()
