
import os
import json
from typing import Any, Optional, Dict
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 3600  # Cache entries expire after 1 hour

async def init_redis_pool():
    """Initialize Redis connection pool"""
    return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

async def get_cache(redis_client, key: str) -> Optional[Dict[str, Any]]:
    """Get value from Redis cache"""
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Redis get error: {str(e)}")
        return None

async def set_cache(redis_client, key: str, value: Dict[str, Any], ttl: int = CACHE_TTL) -> bool:
    """Set value in Redis cache"""
    try:
        await redis_client.set(key, json.dumps(value), ex=ttl)
        return True
    except Exception as e:
        print(f"Redis set error: {str(e)}")
        return False

def make_cache_key(guess: str, word: str, persona: str) -> str:
    """Create a consistent cache key"""
    return f"verdict:{guess.lower()}:{word.lower()}:{persona.lower()}"

# Rate limiting functions
async def check_rate_limit(redis_client, ip: str, limit: int = 100, window: int = 60) -> bool:
    """Check if IP has exceeded rate limit"""
    key = f"ratelimit:{ip}:{int(time.time()) // window}"
    count = await redis_client.incr(key)
    
    if count == 1:
        await redis_client.expire(key, window)
    
    return count <= limit

import time
