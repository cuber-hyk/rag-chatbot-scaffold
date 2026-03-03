"""
Session Service

Handles session management operations.
"""

from src.repositories.session_repository import SessionRepository


class SessionService:
    """Service for session operations"""

    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def get_session(self, thread_id: str):
        """Get session by thread ID"""
        return await self.session_repo.get_session(thread_id)

    async def delete_session(self, thread_id: str) -> bool:
        """Delete a session"""
        return await self.session_repo.delete_session(thread_id)

    async def list_sessions(self) -> list:
        """List all sessions"""
        return await self.session_repo.get_all_sessions()
