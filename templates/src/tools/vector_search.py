"""
Vector Search Tool
"""

from langchain_core.tools import tool
from src.core.config.settings import get_settings

# Singleton instance
_vector_repo = None


@tool
async def vector_search(query: str, top_k: int = 5) -> str:
    """
    Search for information in uploaded documents using vector similarity.

    Args:
        query: The search query
        top_k: Number of results to return (default: 5)

    Returns:
        Relevant document chunks with sources
    """
    global _vector_repo
    settings = get_settings()

    # Create repository instance once
    if _vector_repo is None:
        from src.repositories.weaviate_repository import WeaviateRepository
        from src.repositories.qdrant_repository import QdrantRepository
        from src.repositories.pinecone_repository import PineconeRepository

        if settings.vector_db_provider == "weaviate":
            _vector_repo = WeaviateRepository()
        elif settings.vector_db_provider == "qdrant":
            _vector_repo = QdrantRepository()
        elif settings.vector_db_provider == "pinecone":
            _vector_repo = PineconeRepository()
        else:
            return "Vector database not configured"

        await _vector_repo.initialize()

    results = await _vector_repo.search(
        query=query,
        collection_name=settings.vector_db_collection,
        top_k=top_k
    )

    if not results:
        return "No relevant information found in the document database."

    # Format results
    formatted = []
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("filename", "Unknown")
        chunk_idx = doc.metadata.get("chunk_index", 0)
        formatted.append(f"{i}. [{source} - chunk {chunk_idx}]: {doc.page_content}")

    return "\n\n".join(formatted)
