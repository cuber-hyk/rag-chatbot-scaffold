"""
Vector Repository Interface

Abstract base class for vector database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from .base import BaseRepository


class VectorRepository(BaseRepository):
    """Abstract vector repository interface"""

    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str,
        **kwargs
    ) -> int:
        """
        Add documents to vector store

        Args:
            documents: List of LangChain documents
            collection_name: Name of the collection
            **kwargs: Additional parameters

        Returns:
            Number of documents added
        """

    @abstractmethod
    async def search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        **kwargs
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Search query
            collection_name: Name of the collection
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of matching documents
        """

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection

        Args:
            collection_name: Name of the collection

        Returns:
            True if deleted successfully
        """

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if vector database is healthy"""
        return True

    async def find_by_filename(
        self,
        filename: str,
        collection_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a document by filename

        Args:
            filename: Document filename
            collection_name: Name of the collection

        Returns:
            Document info dict with document_id, filename, content_hash, etc. or None
        """
        return None

    async def find_by_content_hash(
        self,
        content_hash: str,
        collection_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a document by content hash

        Args:
            content_hash: SHA256 hash of document content
            collection_name: Name of the collection

        Returns:
            Document info dict with document_id, filename, content_hash, etc. or None
        """
        return None
