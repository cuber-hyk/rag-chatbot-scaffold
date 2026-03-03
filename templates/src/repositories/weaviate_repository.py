"""
Weaviate Repository

Implements VectorRepository using Weaviate v4 Python client.
"""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.classes.config import Configure, Property, DataType
from src.repositories.vector_repository import VectorRepository
from src.core.config.settings import get_settings
from src.core.config.llm import LLMConfig


class WeaviateRepository(VectorRepository):
    """Weaviate vector database repository (v4 client)"""

    def __init__(self):
        self._client: Optional[weaviate.WeaviateClient] = None
        self.settings = get_settings()
        self._llm_config = LLMConfig()

    async def initialize(self) -> None:
        """Initialize Weaviate connection using v4 client"""
        url = self.settings.weaviate_url
        api_key = self.settings.weaviate_api_key

        # Parse URL to extract host and port
        if url.startswith("http://"):
            url = url.replace("http://", "")
        elif url.startswith("https://"):
            url = url.replace("https://", "")

        # Split host and port
        if ":" in url:
            host, port = url.split(":")
            port = int(port)
        else:
            host = url
            port = 8080

        # Connect using v4 client
        if api_key and api_key.strip() and api_key.lower() != "none":
            self._client = weaviate.connect_to_local(
                host=host, port=port, grpc_port=50051,
                auth_credentials=AuthApiKey(api_key)
            )
        else:
            self._client = weaviate.connect_to_local(
                host=host, port=port, grpc_port=50051
            )

    async def add_documents(
        self,
        documents: List[Document],
        collection_name: str,
        **kwargs
    ) -> int:
        """Add documents to Weaviate using v4 API"""
        if not self._client:
            await self.initialize()

        # Check/create collection
        if not self._client.collections.exists(collection_name):
            self._client.collections.create(
                name=collection_name,
                properties=[
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="filename", data_type=DataType.TEXT),
                    Property(name="chunk_index", data_type=DataType.INT),
                ],
                vectorizer_config=Configure.Vectorizer.none()
            )

        # Get embedding function
        embedding_func = self._get_embedding_function()

        # Get collection
        collection = self._client.collections.get(collection_name)

        # Batch insert documents
        with collection.batch.dynamic() as batch:
            for idx, doc in enumerate(documents):
                text = doc.page_content
                embedding = embedding_func(text)

                properties = {
                    "text": text,
                    "document_id": doc.metadata.get("document_id", ""),
                    "filename": doc.metadata.get("filename", ""),
                    "chunk_index": idx,
                }

                batch.add_object(
                    properties=properties,
                    vector=embedding
                )

        return len(documents)

    async def search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        **kwargs
    ) -> List[Document]:
        """Search in Weaviate using v4 API"""
        if not self._client:
            await self.initialize()

        # Get collection
        collection = self._client.collections.get(collection_name)

        # Get query embedding
        embedding_func = self._get_embedding_function()
        query_vector = embedding_func(query)

        # Search
        results = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k
        )

        # Convert to LangChain Documents
        documents = []
        for obj in results.objects:
            props = obj.properties
            documents.append(Document(
                page_content=props.get("text", ""),
                metadata=props
            ))

        return documents

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection from Weaviate

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        if not self._client:
            await self.initialize()

        try:
            # v4 client API
            if self._client.collections.exists(collection_name):
                self._client.collections.delete(collection_name)
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """
        Close Weaviate connection

        In v4 client, the close() method is available on the client.
        """
        if self._client:
            self._client.close()
        self._store = None
        self._client = None

    async def health_check(self) -> bool:
        """Check Weaviate health"""
        if not self._client:
            return False

        try:
            # v4 client uses is_ready() instead of is_live()
            return self._client.is_ready()
        except Exception:
            return False

    async def list_documents(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        List all unique documents in the collection

        Args:
            collection_name: Name of the collection

        Returns:
            List of document summaries with document_id, filename, chunk_count
        """
        if not self._client:
            await self.initialize()

        try:
            # Get the collection
            collection = self._client.collections.get(collection_name)

            # Query all objects and extract unique document_ids
            documents_map: Dict[str, Dict[str, Any]] = {}

            # Iterate through all objects in the collection
            for object_data in collection.iterator():
                props = object_data.properties
                if props and "document_id" in props:
                    doc_id = props["document_id"]
                    if doc_id not in documents_map:
                        documents_map[doc_id] = {
                            "document_id": doc_id,
                            "filename": props.get("filename", "unknown"),
                            "chunk_count": 0,
                        }
                    documents_map[doc_id]["chunk_count"] += 1

            return list(documents_map.values())

        except Exception:
            return []

    async def delete_document(self, document_id: str, collection_name: str) -> bool:
        """
        Delete all chunks associated with a document

        Args:
            document_id: Document ID to delete
            collection_name: Name of the collection

        Returns:
            True if successful
        """
        if not self._client:
            await self.initialize()

        try:
            # Get the collection
            collection = self._client.collections.get(collection_name)

            # Weaviate v4: Query by document_id and delete matching objects
            # Using batch delete with where filter
            from weaviate.classes import Object

            # Get all objects with this document_id
            to_delete = []
            for object_data in collection.iterator():
                props = object_data.properties
                if props and props.get("document_id") == document_id:
                    to_delete.append(object_data.uuid)

            # Delete each object
            for uuid in to_delete:
                collection.data.delete_by_uuid(uuid)

            return len(to_delete) > 0

        except Exception:
            return False

    async def get_document_chunks(
        self,
        document_id: str,
        collection_name: str
    ) -> List[Document]:
        """
        Get all chunks for a specific document

        Args:
            document_id: Document ID
            collection_name: Name of the collection

        Returns:
            List of document chunks
        """
        if not self._client:
            await self.initialize()

        try:
            # Get the collection
            collection = self._client.collections.get(collection_name)

            chunks = []
            for object_data in collection.iterator():
                props = object_data.properties
                if props and props.get("document_id") == document_id:
                    # Convert Weaviate object to LangChain Document
                    # The text content is stored in a property (depends on schema)
                    # For LangChain Weaviate, it's typically in "text" or similar
                    text_content = props.get("text", "")

                    chunks.append(Document(
                        page_content=text_content,
                        metadata=props
                    ))

            return chunks

        except Exception:
            return []

    async def count_documents(self, collection_name: str) -> int:
        """
        Count the number of unique documents in the collection

        Args:
            collection_name: Name of the collection

        Returns:
            Number of unique documents
        """
        docs = await self.list_documents(collection_name)
        return len(docs)

    async def count_chunks(self, collection_name: str) -> int:
        """
        Count the total number of chunks in the collection

        Args:
            collection_name: Name of the collection

        Returns:
            Total number of chunks
        """
        if not self._client:
            await self.initialize()

        try:
            # Get the collection
            collection = self._client.collections.get(collection_name)

            # Count all objects
            count = 0
            for _ in collection.iterator():
                count += 1

            return count

        except Exception:
            return 0

    def _get_embedding_function(self):
        """Get embedding function that returns vector for given text"""
        embeddings = self._get_embedding()
        return lambda text: embeddings.embed_query(text)

    def _get_embedding(self):
        """Get embedding model instance"""
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=self.settings.embedding_model,
            api_key=self._llm_config._get_api_key(),
            base_url=self.settings.embedding_base_url
        )
