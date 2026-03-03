"""
Document Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    success: bool = Field(..., description="Whether upload was successful")
    document_id: Optional[str] = Field(None, description="Document ID (if successful)")
    chunks_added: Optional[int] = Field(None, description="Number of chunks added (if successful)")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error type if failed")
    existing_document_id: Optional[str] = Field(None, description="Existing document ID if conflict")


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
