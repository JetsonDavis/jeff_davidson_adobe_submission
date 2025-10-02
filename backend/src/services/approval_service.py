"""
Service for managing approval workflow.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
import uuid
from datetime import datetime

from ..models.approval import Approval
from ..models.creative import Creative
from ..models.idea import Idea


class ApprovalService:
    """Handles approval workflow for creatives"""
    
    def get_approval_by_creative(self, db: Session, creative_id: uuid.UUID) -> Optional[Approval]:
        """Get approval record for a creative"""
        return db.query(Approval).filter(Approval.creative_id == creative_id).first()
    
    def get_approval_by_creative_or_404(self, db: Session, creative_id: uuid.UUID) -> Approval:
        """Get approval record or raise 404"""
        approval = self.get_approval_by_creative(db, creative_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval record not found")
        return approval
    
    def approve_creative(self, db: Session, creative_id: uuid.UUID) -> Approval:
        """
        Grant creative approval.
        
        Args:
            db: Database session
            creative_id: Creative UUID
        
        Returns:
            Updated Approval instance
        
        Raises:
            HTTPException: 404 if creative/approval not found
        """
        approval = self.get_approval_by_creative_or_404(db, creative_id)
        
        approval.creative_approved = True
        approval.creative_approved_at = datetime.utcnow()
        approval.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(approval)
        
        return approval
    
    def approve_regional(self, db: Session, creative_id: uuid.UUID) -> Approval:
        """
        Grant regional approval.
        
        Args:
            db: Database session
            creative_id: Creative UUID
        
        Returns:
            Updated Approval instance
        
        Raises:
            HTTPException: 404 if creative/approval not found
        """
        approval = self.get_approval_by_creative_or_404(db, creative_id)
        
        approval.regional_approved = True
        approval.regional_approved_at = datetime.utcnow()
        approval.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(approval)
        
        return approval
    
    def deploy_creative(self, db: Session, creative_id: uuid.UUID) -> Approval:
        """
        Deploy creative (requires creative approval, and regional approval if not US).
        
        Args:
            db: Database session
            creative_id: Creative UUID
        
        Returns:
            Updated Approval instance
        
        Raises:
            HTTPException: 400 if approvals not granted, 404 if not found
        """
        approval = self.get_approval_by_creative_or_404(db, creative_id)
        
        # Check if already deployed
        if approval.deployed:
            raise HTTPException(
                status_code=400,
                detail="Creative already deployed"
            )
        
        # Get creative and check region
        creative = db.query(Creative).filter(Creative.id == creative_id).first()
        if not creative:
            raise HTTPException(status_code=404, detail="Creative not found")
        
        # Get region from idea
        idea = db.query(Idea).filter(Idea.id == creative.idea_id).first()
        is_us = idea and idea.region == 'US'
        
        # Check approvals - regional not required for US
        if not approval.creative_approved:
            raise HTTPException(
                status_code=400,
                detail="Creative approval required before deployment"
            )
        
        if not is_us and not approval.regional_approved:
            raise HTTPException(
                status_code=400,
                detail="Both creative and regional approvals required before deployment"
            )
        
        approval.deployed = True
        approval.deployed_at = datetime.utcnow()
        approval.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(approval)
        
        return approval
    
    def toggle_creative_approval(self, db: Session, creative_id: uuid.UUID) -> Approval:
        """
        Toggle creative approval on/off.
        Cannot toggle if already deployed.
        """
        approval = self.get_approval_by_creative_or_404(db, creative_id)
        
        if approval.deployed:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify approval - creative already deployed"
            )
        
        approval.creative_approved = not approval.creative_approved
        approval.creative_approved_at = datetime.utcnow() if approval.creative_approved else None
        approval.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(approval)
        
        return approval
    
    def toggle_regional_approval(self, db: Session, creative_id: uuid.UUID) -> Approval:
        """
        Toggle regional approval on/off.
        Cannot toggle if already deployed.
        """
        approval = self.get_approval_by_creative_or_404(db, creative_id)
        
        if approval.deployed:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify approval - creative already deployed"
            )
        
        approval.regional_approved = not approval.regional_approved
        approval.regional_approved_at = datetime.utcnow() if approval.regional_approved else None
        approval.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(approval)
        
        return approval
    
    def can_deploy(self, approval: Approval) -> bool:
        """Check if creative can be deployed"""
        return (
            approval.creative_approved and
            approval.regional_approved and
            not approval.deployed
        )


# Singleton instance
approval_service = ApprovalService()
