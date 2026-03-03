"""
Pinecone Repository

Implementation of VectorRepository using Pinecone from langchain_pinecone.
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from src.repositories.vector_repository import VectorRepository
from src.core.config.settings import get_settings


class PineconeRepository(VectorRepository):
    """Pinecone vector database repository"""

    def __init__(self):
        self._store: Optional[PineconeVectorStore] = None
        self._index_name: Optional[str] = None
        self.settings = get_settings()

    async def initialize(self) -> None:
        """Initialize Pinecone connection"""
        if self._store is None:
            from pinecone import Pinecone
            self._client = Pinecone(
                api_key=self.settings.pinecone_api_key
            )

    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str,
        **kwargs
    ) -> int:
        """
        Add documents to Pinecone

        Args:
            documents: List of LangChain documents
            collection_name: Name of the collection (used as index name)
            **kwargs: Additional parameters

        Returns:
            Number of documents added
        """
        if self._client is None:
            await self.initialize()

        self._index_name = collection_name

        # Check if index exists
        if self._index_name not in [idx.name for idx in self._client.list_indexes()]:
            # Create index if it doesn't exist
            self._client.create_index(
                name=collection_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=self.settings.pinecone_cloud,
                    region=self.settings.pinecone_region
                )
            )

        # Add documents
        PineconeVectorStore.from_documents(
            documents=documents,
            index_name=collection_name,
            embedding=self._get_embedding()
        )

        return len(documents)

    async def search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        **kwargs
    ) -> List[Document]:
        """
        Search in Pinecone

        Args:
            query: Search query
            collection_name: Name of the collection
            top_k: Number of results to return
            **kwargs: Additional search parameters

        Returns:
            List of matching documents
        """
        if self._client is None:
            await self.initialize()

        self._index_name = collection_name

        # Create vector store
        store = PineconeVectorStore(
            index_name=collection_name,
            embedding=self._get_embedding()
        )

        results = await store.asimilarity_search(
            query=query,
            k=top_k,
            **kwargs
        )

        return results

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection from Pinecone

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        if self._client is None:
            await self.initialize()

        try:
            self._client.delete_index(collection_name)
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close Pinecone connection"""
        self._client = None
        self._index_name = None

    async def health_check(self) -> bool:
        """Check Pinecone health"""
        if self._client is None:
            return False

        try:
            # List indexes to verify connection
            self._client.list_indexes()
            return True
        except Exception:
            return False

    def _get_embedding(self):
        """Get embedding model instance"""
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=self.settings.embedding_model,
            openai_api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_base_url
        )
