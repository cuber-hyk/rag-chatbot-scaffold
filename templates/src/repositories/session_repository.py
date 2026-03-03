"""
Session Repository

Manages session storage using Redis.
"""

from typing import Optional, List, Dict
import json
import redis.asyncio as redis
from src.repositories.base import BaseRepository
from src.core.config.settings import get_settings


class SessionRepository(BaseRepository):
    """Redis-based session repository"""

    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self.settings = get_settings()

    async def initialize(self) -> None:
        """Initialize Redis connection"""
        self._client = await redis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self) -> None:
        """Close Redis connection"""
        if self._client:
            await self._client.close()

    async def create_session(
        self,
        thread_id: str,
        initial_data: Optional[Dict] = None
    ) -> str:
        """Create a new session"""
        data = initial_data or {"messages": []}
        await self._client.setex(
            f"session:{thread_id}",
            self.settings.session_ttl,
            json.dumps(data)
        )
        return thread_id

    async def get_session(self, thread_id: str) -> Optional[Dict]:
        """Get session data"""
        data = await self._client.get(f"session:{thread_id}")
        if data:
            return json.loads(data)
        return None

    async def update_session(
        self,
        thread_id: str,
        data: Dict
    ) -> bool:
        """Update session data"""
        return await self._client.setex(
            f"session:{thread_id}",
            self.settings.session_ttl,
            json.dumps(data)
        )

    async def delete_session(self, thread_id: str) -> bool:
        """Delete a session"""
        result = await self._client.delete(f"session:{thread_id}")
        return result > 0

    async def session_exists(self, thread_id: str) -> bool:
        """Check if session exists"""
        return await self._client.exists(f"session:{thread_id}") > 0

    async def get_all_sessions(self) -> List[str]:
        """Get all session IDs"""
        pattern = "session:*"
        keys = []
        async for key in self._client.scan_iter(match=pattern):
            keys.append(key.replace("session:", ""))
        return keys
