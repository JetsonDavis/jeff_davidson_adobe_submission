"""
CRUD service for Idea entity with regeneration logic.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import uuid
from datetime import datetime

from ..models.idea import Idea
from ..models.brief import Brief


class IdeaService:
    """Handles CRUD operations and regeneration for ideas"""
    
    def create_idea(
        self,
        db: Session,
        brief_id: uuid.UUID,
        region: str,
        demographic: str,
        content: str,
        language_code: str
    ) -> Idea:
        """
        Create a new idea.
        
        Args:
            db: Database session
            brief_id: Parent brief UUID
            region: Target region
            demographic: Target demographic
            content: LLM-generated idea content
            language_code: Language for the region
        
        Returns:
            Created Idea instance
        """
        idea = Idea(
            brief_id=brief_id,
            region=region,
            demographic=demographic,
            content=content,
            language_code=language_code,
            generation_count=1
        )
        
        db.add(idea)
        db.commit()
        db.refresh(idea)
        
        return idea
    
    def get_idea(self, db: Session, idea_id: uuid.UUID) -> Optional[Idea]:
        """Get idea by ID"""
        return db.query(Idea).filter(Idea.id == idea_id).first()
    
    def get_idea_or_404(self, db: Session, idea_id: uuid.UUID) -> Idea:
        """Get idea by ID or raise 404"""
        idea = self.get_idea(db, idea_id)
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        return idea
    
    def list_ideas_by_brief(self, db: Session, brief_id: uuid.UUID) -> List[Idea]:
        """Get all ideas for a specific brief"""
        return db.query(Idea).filter(Idea.brief_id == brief_id).all()
    
    def regenerate_idea(self, db: Session, idea_id: uuid.UUID, new_content: str) -> Idea:
        """
        Regenerate idea with new content.
        Increments generation_count and updates timestamp.
        
        Args:
            db: Database session
            idea_id: Idea UUID to regenerate
            new_content: New LLM-generated content
        
        Returns:
            Updated Idea instance
        
        Raises:
            HTTPException: 404 if idea not found
        """
        idea = self.get_idea_or_404(db, idea_id)
        
        idea.content = new_content
        idea.generation_count += 1
        idea.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(idea)
        
        return idea
    
    def delete_idea(self, db: Session, idea_id: uuid.UUID) -> bool:
        """Delete idea by ID"""
        idea = self.get_idea(db, idea_id)
        if not idea:
            return False
        
        db.delete(idea)
        db.commit()
        return True


# Singleton instance
idea_service = IdeaService()
