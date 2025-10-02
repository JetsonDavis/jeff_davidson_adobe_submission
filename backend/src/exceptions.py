"""
Custom exception classes for the application.
"""
from fastapi import HTTPException


class BriefNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Brief not found")


class AssetNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Asset not found")


class IdeaNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Idea not found")


class CreativeNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Creative not found")


class ApprovalNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Approval record not found")


class InvalidFileTypeException(HTTPException):
    def __init__(self, allowed_types: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {allowed_types}"
        )


class FileTooLargeException(HTTPException):
    def __init__(self, max_size_mb: int = 10):
        super().__init__(
            status_code=400,
            detail=f"File too large. Maximum size: {max_size_mb}MB"
        )


class DeploymentRequiresApprovalsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Both creative and regional approvals required before deployment"
        )


class AlreadyDeployedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Creative already deployed"
        )
