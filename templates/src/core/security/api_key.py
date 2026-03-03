"""API Key Authentication"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.core.config.settings import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key from header"""
    settings = get_settings()
    configured_key = settings.api_key

    if not configured_key or configured_key.lower() == "none":
        return None

    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing. Provide X-API-Key header."
        )

    if api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    return api_key
