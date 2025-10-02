"""
API endpoints for Approval workflow management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from ..db import get_db
from ..schemas.approval import ApprovalResponse
from ..services.approval_service import approval_service

router = APIRouter(prefix="/creatives", tags=["approvals"])


@router.post("/{creative_id}/approve-creative", response_model=ApprovalResponse)
def approve_creative(creative_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Toggle creative approval for a creative.
    Click once to approve, click again to remove approval.
    Cannot toggle if already deployed.
    """
    approval = approval_service.toggle_creative_approval(db, creative_id)
    return approval


@router.post("/{creative_id}/approve-regional", response_model=ApprovalResponse)
def approve_regional(creative_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Toggle regional approval for a creative.
    Click once to approve, click again to remove approval.
    Cannot toggle if already deployed.
    """
    approval = approval_service.toggle_regional_approval(db, creative_id)
    return approval


@router.post("/{creative_id}/deploy", response_model=ApprovalResponse)
def deploy_creative(creative_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Deploy creative to production.
    Requires both creative and regional approvals.
    Once deployed, creative cannot be redeployed.
    """
    approval = approval_service.deploy_creative(db, creative_id)
    return approval
