"""
Chat Request/Response Schemas
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Chat request model"""
    query: str = Field(..., description="User query or message", min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str = Field(..., description="AI response")
    thread_id: str = Field(..., description="Session thread ID")


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str = Field(..., description="Partial response content")
    done: bool = Field(default=False, description="Whether the response is complete")
