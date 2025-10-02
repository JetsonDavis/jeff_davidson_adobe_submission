"""
CRUD service for Creative entity with regeneration logic.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import uuid
from datetime import datetime

from ..models.creative import Creative
from ..models.approval import Approval
from ..models.idea import Idea


class CreativeService:
    """Handles CRUD operations and regeneration for creatives"""
    
    def create_creative(
        self,
        db: Session,
        idea_id: uuid.UUID,
        file_path: str,
        mime_type: str,
        file_size: int,
        aspect_ratio: str = "1:1",
        firefly_job_id: Optional[str] = None
    ) -> Creative:
        """
        Create a new creative and its associated approval record.
        
        Args:
            db: Database session
            idea_id: Parent idea UUID
            file_path: Filesystem path to creative image
            mime_type: MIME type of image
            file_size: File size in bytes
            firefly_job_id: Optional Firefly job ID
        
        Returns:
            Created Creative instance with approval relationship
        """
        creative = Creative(
            idea_id=idea_id,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            aspect_ratio=aspect_ratio,
            firefly_job_id=firefly_job_id,
            generation_count=1
        )
        
        db.add(creative)
        db.flush()  # Get creative ID before creating approval
        
        # Create associated approval record
        approval = Approval(
            creative_id=creative.id,
            creative_approved=False,
            regional_approved=False,
            deployed=False
        )
        
        db.add(approval)
        db.commit()
        db.refresh(creative)
        
        return creative
    
    def get_creative(self, db: Session, creative_id: uuid.UUID) -> Optional[Creative]:
        """Get creative by ID"""
        return db.query(Creative).filter(Creative.id == creative_id).first()
    
    def get_creative_or_404(self, db: Session, creative_id: uuid.UUID) -> Creative:
        """Get creative by ID or raise 404"""
        creative = self.get_creative(db, creative_id)
        if not creative:
            raise HTTPException(status_code=404, detail="Creative not found")
        return creative
    
    def list_creatives(
        self,
        db: Session,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Creative]:
        """
        List creatives with optional status filtering.
        
        Args:
            db: Database session
            status: Optional filter ('pending', 'approved', 'deployed')
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of Creative instances
        """
        query = db.query(Creative).join(Approval)
        
        if status == "pending":
            query = query.filter(Approval.deployed == False)
        elif status == "approved":
            query = query.filter(
                Approval.creative_approved == True,
                Approval.regional_approved == True,
                Approval.deployed == False
            )
        elif status == "deployed":
            query = query.filter(Approval.deployed == True)
        
        return query.order_by(Creative.created_at.desc()).offset(skip).limit(limit).all()
    
    def regenerate_creative(
        self,
        db: Session,
        creative_id: uuid.UUID,
        new_file_path: str,
        new_file_size: int,
        new_firefly_job_id: Optional[str] = None
    ) -> Creative:
        """
        Regenerate creative with new image.
        Increments generation_count, resets approvals to false.
        
        Args:
            db: Database session
            creative_id: Creative UUID to regenerate
            new_file_path: New filesystem path
            new_file_size: New file size
            new_firefly_job_id: Optional new Firefly job ID
        
        Returns:
            Updated Creative instance
        
        Raises:
            HTTPException: 404 if creative not found
        """
        creative = self.get_creative_or_404(db, creative_id)
        
        # Update creative
        creative.file_path = new_file_path
        creative.file_size = new_file_size
        creative.firefly_job_id = new_firefly_job_id
        creative.generation_count += 1
        creative.updated_at = datetime.utcnow()
        
        # Reset approvals
        if creative.approval:
            creative.approval.creative_approved = False
            creative.approval.creative_approved_at = None
            creative.approval.regional_approved = False
            creative.approval.regional_approved_at = None
            creative.approval.deployed = False
            creative.approval.deployed_at = None
            creative.approval.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(creative)
        
        return creative
    
    def delete_creative(self, db: Session, creative_id: uuid.UUID) -> bool:
        """Delete creative by ID (cascades to approval)"""
        creative = self.get_creative(db, creative_id)
        if not creative:
            return False
        
        db.delete(creative)
        db.commit()
        return True


# Singleton instance
creative_service = CreativeService()
