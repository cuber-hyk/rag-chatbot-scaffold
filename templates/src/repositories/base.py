"""
Base Repository Interface

Defines the abstract interface for all repositories.
"""

from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """Base repository interface"""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the repository connection"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the repository connection"""
        pass
