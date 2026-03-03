"""
my-rag-chatbot - Application Entry Point

RAG Chatbot with vector search and network capabilities.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1 import router as api_v1_router
from src.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.project_name}


app.include_router(api_v1_router, prefix=f"/api/{settings.api_version_prefix}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.api_host, port=settings.api_port, reload=True)
