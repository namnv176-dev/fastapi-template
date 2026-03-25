import logging

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

LOGGER = logging.getLogger(__name__)


async def check_database_health(db: AsyncSession) -> bool:
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        LOGGER.exception(f"Database health check failed with error: {e}")
        return False


async def check_redis_health(redis: Redis) -> bool:
    try:
        await redis.ping()
        return True
    except Exception as e:
        LOGGER.exception(f"Redis health check failed with error: {e}")
        return False


async def check_third_party_health() -> bool:
    """Check connectivity to 3rd party services."""
    try:
        # Placeholder: Add actual 3rd party connectivity checks here
        # e.g., using httpx to check external API status
        return True
    except Exception as e:
        LOGGER.exception(f"3rd party health check failed with error: {e}")
        return False
