"""
Session Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Any


class SessionResponse(BaseModel):
    """Session response"""
    thread_id: str = Field(..., description="Session thread ID")
    data: Any = Field(..., description="Session data")


class SessionDeleteResponse(BaseModel):
    """Session deletion response"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")


class SessionListResponse(BaseModel):
    """Session list response"""
    sessions: List[str] = Field(default_factory=list, description="List of session IDs")
