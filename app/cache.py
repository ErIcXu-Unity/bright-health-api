import time
from typing import Any, Optional

_cache: dict[str, tuple[Any, float]] = {}


def get(key: str) -> Optional[Any]:
    if key in _cache:
        value, expires_at = _cache[key]
        if time.time() < expires_at:
            return value
        del _cache[key]
    return None


def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    expires_at = time.time() + ttl_seconds
    _cache[key] = (value, expires_at)


def clear() -> None:
    _cache.clear()
