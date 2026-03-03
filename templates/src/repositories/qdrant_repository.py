"""
Qdrant Vector Repository

Implementation of VectorRepository using Qdrant from langchain_community.vectorstores.
"""

from typing import List, Optional
from langchain_community.vectorstores import Qdrant as QdrantVectorStore
from qdrant_client import QdrantClient, models
from src.repositories.vector_repository import VectorRepository
from src.core.config.settings import get_settings


class QdrantRepository(VectorRepository):
    """Qdrant vector database repository"""

    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._store: Optional[QdrantVectorStore] = None
        self.settings = get_settings()

    async def initialize(self) -> None:
        """Initialize Qdrant client"""
        if self._client is None:
            self._client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key or None
            )

    async def add_documents(
        self,
        documents: List,
        collection_name: str,
        **kwargs
    ) -> int:
        """
        Add documents to Qdrant

        Args:
            documents: List of LangChain documents
            collection_name: Name of the collection
            **kwargs: Additional parameters

        Returns:
            Number of documents added
        """
        if not self._client:
            await self.initialize()

        from src.core.config.llm import LLMConfig
        llm_config = LLMConfig()
        embedding_model = llm_config.get_embedding_model()

        # Create vector store
        self._store = QdrantVectorStore.from_documents(
            documents=documents,
            client=self._client,
            embedding=embedding_model,
            collection_name=collection_name,
            **kwargs
        )

        return len(documents)

    async def search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        **kwargs
    ) -> List:
        """
        Search Qdrant for similar documents

        Args:
            query: Search query
            collection_name: Name of the collection
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of matching documents
        """
        if not self._store:
            from src.core.config.llm import LLMConfig
            llm_config = LLMConfig()
            embedding_model = llm_config.get_embedding_model()

            # Create store for existing collection
            self._store = QdrantVectorStore(
                client=self._client,
                collection_name=collection_name,
                embedding=embedding_model
            )

        results = await self._store.asimilarity_search(
            query=query,
            k=top_k,
            **kwargs
        )

        return results

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection from Qdrant

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        if not self._client:
            await self.initialize()

        try:
            self._client.delete_collection(collection_name)
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Qdrant connection"""
        if self._client:
            # QdrantClient doesn't have explicit close method
            self._client = None
        self._store = None
        self._client = None

    async def health_check(self) -> bool:
        """Check Qdrant health"""
        if not self._store:
            return False

        try:
            # Check if we can list collections
            self._client.get_collections()
            return True
        except Exception:
            return False
