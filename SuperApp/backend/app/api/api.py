"""
API router for all endpoints.
"""

from fastapi import APIRouter

from app.api.endpoints import auth, content, chat, rag, resume

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"]) 