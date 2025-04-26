import aioredis
import os
from dotenv import load_dotenv

load_dotenv()

async def init_redis_pool():
    """Initialize and return a Redis connection pool."""
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    return await aioredis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True
    )

async def cache_set(redis, key: str, value: str, expire: int = 3600):
    """Set a value in the cache with expiration."""
    await redis.set(key, value, ex=expire)

async def cache_get(redis, key: str):
    """Get a value from the cache."""
    return await redis.get(key)

async def cache_delete(redis, key: str):
    """Delete a key from the cache."""
    await redis.delete(key)

async def cache_exists(redis, key: str):
    """Check if a key exists in the cache."""
    return await redis.exists(key)