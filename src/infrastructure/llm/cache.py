import langchain
from langchain_community.cache import RedisCache
from redis import Redis

from src.core.config import settings


def setup_llm_cache() -> None:
    """
    Setup LangChain global cache using Redis if configured.
    """
    if settings.REDIS_CACHE_HOST:
        try:
            # Note: Using synchronous Redis client for LangChain's default RedisCache
            langchain.llm_cache = RedisCache(  # type: ignore[attr-defined]
                redis_=Redis(
                    host=settings.REDIS_CACHE_HOST,
                    port=settings.REDIS_CACHE_PORT,
                    decode_responses=False,
                )
            )
        except Exception as e:
            # Fallback to no cache or log error
            print(f"Failed to setup LLM Redis cache: {e}")
