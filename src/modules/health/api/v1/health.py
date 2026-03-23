from fastapi import APIRouter

from src.core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.ENVIRONMENT}
