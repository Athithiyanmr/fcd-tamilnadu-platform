"""Health-check endpoint."""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "FCD Tamil Nadu Platform",
        "titiler": settings.TITILER_URL,
        "storage": settings.STORAGE_BACKEND,
    }
