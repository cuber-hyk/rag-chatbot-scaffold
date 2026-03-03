"""
Vector Search Tool
"""

from langchain_core.tools import tool
from src.core.config.settings import get_settings


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
    from src.api.dependencies import get_vector_repository

    settings = get_settings()
    vector_repo = await get_vector_repository.__anext__()

    results = await vector_repo.search(
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
