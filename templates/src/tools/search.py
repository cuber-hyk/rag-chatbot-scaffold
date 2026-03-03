"""
Web Search Tool
"""

from langchain_core.tools import tool
from src.core.config.settings import get_settings


@tool
async def search(query: str, max_results: int = 5) -> str:
    """
    Search the internet for current information.

    Args:
        query: The search query
        max_results: Number of results to return (default: 5)

    Returns:
        Search results with sources
    """
    settings = get_settings()

    if settings.search_provider == "duckduckgo":
        return await _duckduckgo_search(query, max_results)
    elif settings.search_provider == "tavily":
        return await _tavily_search(query, max_results)
    else:
        return "Search tool not configured"


async def _duckduckgo_search(query: str, max_results: int) -> str:
    """Search using DuckDuckGo via LangChain"""
    from langchain_community.tools import DuckDuckGoSearchResults

    search_engine = DuckDuckGoSearchResults(max_results=max_results)
    return search_engine.invoke(query)


async def _tavily_search(query: str, max_results: int) -> str:
    """Search using Tavily"""
    from tavily import TavilyClient

    client = TavilyClient(api_key=get_settings().tavily_api_key)

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic"
    )

    results = []
    for result in response.get("results", []):
        results.append(f"- {result.get('title')}: {result.get('url')}")
        results.append(f"  {result.get('content', '')}")

    return "\n".join(results) if results else "No results found"
