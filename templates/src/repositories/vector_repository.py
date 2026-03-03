"""
Vector Repository Interface

Abstract base class for vector database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
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
