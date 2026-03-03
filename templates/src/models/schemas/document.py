"""
Document Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: str = Field(..., description="Document ID")
    chunks_added: int = Field(..., description="Number of chunks added")
    message: str = Field(..., description="Status message")


class DocumentInfo(BaseModel):
    """Document information"""
    document_id: str
    filename: str
    content_type: str
    chunk_count: int
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    """Document list response"""
    documents: List[DocumentInfo] = Field(default_factory=list)


class DocumentDeleteResponse(BaseModel):
    """Document deletion response"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
