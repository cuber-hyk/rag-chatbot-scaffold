"""
Session API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_session_service
from src.core.security.api_key import verify_api_key
from src.models.schemas.session import (
    SessionResponse,
    SessionDeleteResponse,
    SessionListResponse
)

router = APIRouter()


@router.get("/{thread_id}", response_model=SessionResponse)
async def get_session(
    thread_id: str,
    session_service = Depends(get_session_service),
    _: str = Depends(verify_api_key)
):
    """
    Get session details by thread ID

    Args:
        thread_id: Session thread ID
        session_service: Session service instance

    Returns:
        Session details
    """
    session = await session_service.get_session(thread_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        thread_id=thread_id,
        data=session
    )


@router.delete("/{thread_id}", response_model=SessionDeleteResponse)
async def delete_session(
    thread_id: str,
    session_service = Depends(get_session_service),
    _: str = Depends(verify_api_key)
):
    """
    Delete a session

    Args:
        thread_id: Session thread ID
        session_service: Session service instance

    Returns:
        Deletion response
    """
    success = await session_service.delete_session(thread_id)
    return SessionDeleteResponse(
        success=success,
        message="Session deleted successfully" if success else "Session not found"
    )


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    session_service = Depends(get_session_service),
    _: str = Depends(verify_api_key)
):
    """
    List all active sessions

    Returns:
        List of session IDs
    """
    sessions = await session_service.list_sessions()
    return SessionListResponse(sessions=sessions)
