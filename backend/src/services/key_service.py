"""
Service for managing application settings (key-value pairs).
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime

from ..models.key import Key


class KeyService:
    """Handles key-value settings storage"""
    
    def get_value(self, db: Session, key: str) -> Optional[str]:
        """Get a single value by key"""
        key_obj = db.query(Key).filter(Key.key == key).first()
        return key_obj.value if key_obj else None
    
    def get_all(self, db: Session) -> Dict[str, str]:
        """Get all key-value pairs as a dictionary"""
        keys = db.query(Key).all()
        return {k.key: k.value for k in keys}
    
    def set_value(self, db: Session, key: str, value: str) -> Key:
        """Set a single key-value pair (upsert)"""
        key_obj = db.query(Key).filter(Key.key == key).first()
        
        if key_obj:
            # Update existing
            key_obj.value = value
            key_obj.updated_at = datetime.utcnow()
        else:
            # Create new
            key_obj = Key(key=key, value=value)
            db.add(key_obj)
        
        db.commit()
        db.refresh(key_obj)
        return key_obj
    
    def set_multiple(self, db: Session, settings: Dict[str, str]) -> Dict[str, str]:
        """Set multiple key-value pairs"""
        for key, value in settings.items():
            self.set_value(db, key, value)
        
        return self.get_all(db)
    
    def delete_value(self, db: Session, key: str) -> bool:
        """Delete a key-value pair"""
        key_obj = db.query(Key).filter(Key.key == key).first()
        if key_obj:
            db.delete(key_obj)
            db.commit()
            return True
        return False


# Singleton instance
key_service = KeyService()
