"""
File handling service for upload, validation, and deletion operations.
"""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException


class FileHandler:
    """Handles file upload, validation, and deletion operations"""
    
    def __init__(self, base_upload_dir: str = "uploads"):
        self.base_upload_dir = Path(base_upload_dir)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Allowed file types
        self.allowed_document_types = {
            "text/plain": "txt",
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
        }
        self.allowed_image_types = {
            "image/jpeg": "jpg",
            "image/png": "png"
        }
    
    async def save_upload_file(
        self,
        file: UploadFile,
        subdirectory: str,
        allowed_types: dict
    ) -> tuple[str, str, int]:
        """
        Save uploaded file to filesystem.
        
        Args:
            file: FastAPI UploadFile object
            subdirectory: Subdirectory within uploads (e.g., 'briefs', 'brand_assets')
            allowed_types: Dict of allowed MIME types to extensions
        
        Returns:
            Tuple of (file_path, original_filename, file_size)
        
        Raises:
            HTTPException: If file validation fails
        """
        # Validate file type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types.keys())}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {self.max_file_size / (1024 * 1024)}MB"
            )
        
        # Generate unique filename
        extension = allowed_types[file.content_type]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        # Create directory if it doesn't exist
        upload_dir = self.base_upload_dir / subdirectory
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / unique_filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path), file.filename, file_size
    
    async def save_document(self, file: UploadFile) -> tuple[str, str, int, str]:
        """
        Save document file (TXT, PDF, Word).
        
        Returns:
            Tuple of (file_path, original_filename, file_size, source_type)
        """
        file_path, original_filename, file_size = await self.save_upload_file(
            file, "briefs", self.allowed_document_types
        )
        source_type = self.allowed_document_types[file.content_type]
        return file_path, original_filename, file_size, source_type
    
    async def save_brand_asset(self, file: UploadFile) -> tuple[str, str, int]:
        """Save brand asset image (JPG or PNG)"""
        return await self.save_upload_file(file, "brand_assets", self.allowed_image_types)
    
    async def save_product_asset(self, file: UploadFile) -> tuple[str, str, int]:
        """Save product asset image (JPG or PNG)"""
        return await self.save_upload_file(file, "product_assets", self.allowed_image_types)
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from filesystem.
        
        Args:
            file_path: Path to file to delete
        
        Returns:
            True if deleted successfully, False if file doesn't exist
        """
        try:
            print(f"🗑️  Attempting to delete file: {file_path}")
            path = Path(file_path)
            if path.exists():
                path.unlink()
                print(f"✅ File deleted successfully: {file_path}")
                return True
            else:
                print(f"⚠️  File does not exist: {file_path}")
            return False
        except Exception as e:
            print(f"❌ Error deleting file {file_path}: {e}")
            return False
    
    def validate_file_exists(self, file_path: str) -> bool:
        """Check if file exists on filesystem"""
        return Path(file_path).exists()


# Singleton instance
file_handler = FileHandler()
