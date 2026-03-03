"""Chat API Endpoints"""

import uuid
from fastapi import APIRouter, Depends, Request, HTTPException
from src.api.dependencies import get_chat_service
from src.core.security.api_key import verify_api_key
from src.models.schemas.chat import ChatResponse

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def chat(
    http_request: Request,
    chat_service=Depends(get_chat_service),
    _: str=Depends(verify_api_key)
):
    """Chat with the RAG-enabled bot. Supports JSON body or URL parameter."""
    # Get query from URL parameter or JSON body
    user_query = http_request.query_params.get("query")
    if not user_query:
        try:
            body = await http_request.json()
            user_query = body.get("query")
        except Exception:
            pass

    if not user_query:
        raise HTTPException(
            status_code=422,
            detail="Query parameter is required. Use {'query': 'message'} in body or ?query=message in URL"
        )

    thread_id = _get_thread_id(http_request)
    response = await chat_service.chat(query=user_query, thread_id=thread_id)

    return ChatResponse(response=response, thread_id=thread_id)


def _get_thread_id(request: Request) -> str:
    """Get or create thread ID from request. Priority: Header > Cookie > Generate new"""
    thread_id = request.headers.get("X-Thread-ID")
    if thread_id:
        return thread_id
    thread_id = request.cookies.get("thread_id")
    if thread_id:
        return thread_id
    return str(uuid.uuid4())
