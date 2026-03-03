"""
API v1 Router
"""

from fastapi import APIRouter
from src.api.v1.endpoints import chat, documents, sessions

router = APIRouter()

# Include all endpoint routers
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
