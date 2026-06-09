import json, asyncio
from typing import Any, Optional

_store: dict = {}
_lock = asyncio.Lock()


async def cache_get(key: str) -> Optional[Any]:
    async with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        import time
        if time.monotonic() > expires_at:
            del _store[key]
            return None
        return value


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    import time
    async with _lock:
        _store[key] = (value, time.monotonic() + ttl_seconds)


async def cache_invalidate(prefix: str) -> None:
    async with _lock:
        keys = [k for k in _store if k.startswith(prefix)]
        for k in keys:
            del _store[k]
