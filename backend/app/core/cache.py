"""Redis cache helpers."""
import json
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import settings

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Optional[dict]:
    r = await get_redis()
    val = await r.get(key)
    return json.loads(val) if val else None


async def cache_set(key: str, value: dict, ttl_seconds: int = 300) -> None:
    r = await get_redis()
    await r.setex(key, ttl_seconds, json.dumps(value))


async def cache_delete(key: str) -> None:
    r = await get_redis()
    await r.delete(key)
