"""
API Dependencies

Dependency injection for API endpoints.
"""

from typing import AsyncGenerator
from fastapi import Depends

from src.repositories.vector_repository import VectorRepository
from src.repositories.session_repository import SessionRepository
from src.repositories.qdrant_repository import QdrantRepository
from src.repositories.weaviate_repository import WeaviateRepository
from src.repositories.pinecone_repository import PineconeRepository
from src.services.chat_service import ChatService
from src.services.document_service import DocumentService
from src.services.session_service import SessionService
from src.core.config.settings import get_settings


# Singleton instances
_vector_repo: VectorRepository = None
_session_repo: SessionRepository = None
_chat_service: ChatService = None
_document_service: DocumentService = None
_session_service: SessionService = None


async def get_vector_repository() -> AsyncGenerator[VectorRepository, None]:
    """Get vector repository instance"""
    global _vector_repo
    if _vector_repo is None:
        settings = get_settings()
        # Import the configured repository
        if settings.vector_db_provider == "qdrant":
            _vector_repo = QdrantRepository()
        elif settings.vector_db_provider == "weaviate":
            _vector_repo = WeaviateRepository()
        elif settings.vector_db_provider == "pinecone":
            _vector_repo = PineconeRepository()
        else:
            raise ValueError(f"Unsupported vector database: {settings.vector_db_provider}")
        await _vector_repo.initialize()
    yield _vector_repo


async def get_session_repository() -> AsyncGenerator[SessionRepository, None]:
    """Get session repository instance"""
    global _session_repo
    if _session_repo is None:
        _session_repo = SessionRepository()
        await _session_repo.initialize()
    yield _session_repo


async def get_chat_service(
    vector_repo: VectorRepository = Depends(get_vector_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
) -> AsyncGenerator[ChatService, None]:
    """Get chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(
            vector_repo=vector_repo,
            session_repo=session_repo
        )
    yield _chat_service


async def get_document_service(
    vector_repo: VectorRepository = Depends(get_vector_repository)
) -> AsyncGenerator[DocumentService, None]:
    """Get document service instance"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService(vector_repo=vector_repo)
    yield _document_service


async def get_session_service(
    session_repo: SessionRepository = Depends(get_session_repository)
) -> AsyncGenerator[SessionService, None]:
    """Get session service instance"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService(session_repo=session_repo)
    yield _session_service
