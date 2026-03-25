from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.health import (
    check_celery_health,
    check_database_health,
    check_redis_health,
    check_third_party_health,
)
from src.core.utils.cache import async_get_redis
from src.db.session import async_get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(async_get_db),
    redis: Redis = Depends(async_get_redis),
) -> Any:
    """Check readiness of the system."""
    db_ok = await check_database_health(db)
    redis_ok = await check_redis_health(redis)
    celery_ok = await check_celery_health()
    third_party_ok = await check_third_party_health()

    is_healthy = db_ok and redis_ok and celery_ok and third_party_ok
    status_str = "healthy" if is_healthy else "unhealthy"

    response_data = {
        "status": status_str,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": {
            "database": "healthy" if db_ok else "unhealthy",
            "redis": "healthy" if redis_ok else "unhealthy",
            "celery": "healthy" if celery_ok else "unhealthy",
            "third_party": "healthy" if third_party_ok else "unhealthy",
        },
    }

    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_data,
        )

    return response_data

@router.post("/health/task")
async def trigger_task(name: str = "test") -> dict[str, str]:
    from src.core.worker.functions import sample_background_task
    task = sample_background_task.delay(name)
    return {"task_id": task.id, "status": "triggered"}
