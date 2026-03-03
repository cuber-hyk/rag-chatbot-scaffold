"""
API Layer

FastAPI endpoints for the application.
"""

from .v1 import router as v1_router

__all__ = ["v1_router"]
