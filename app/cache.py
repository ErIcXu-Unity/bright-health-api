import json
import time
from typing import Any, Optional

import redis

from app.config import settings

_local_cache: dict[str, tuple[Any, float]] = {}
_redis_client: Optional[redis.Redis] = None


def _get_redis() -> Optional[redis.Redis]:
    global _redis_client
    if _redis_client is None and settings.redis_host:
        try:
            _redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True
            )
            _redis_client.ping()
        except redis.ConnectionError:
            _redis_client = None
    return _redis_client


def get(key: str) -> Optional[Any]:
    redis_client = _get_redis()
    if redis_client:
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except redis.ConnectionError:
            pass
    
    if key in _local_cache:
        value, expires_at = _local_cache[key]
        if time.time() < expires_at:
            return value
        del _local_cache[key]
    return None


def set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    if hasattr(value, 'model_dump'):
        value = value.model_dump()
    
    redis_client = _get_redis()
    if redis_client:
        try:
            redis_client.setex(key, ttl_seconds, json.dumps(value, default=str))
            return
        except redis.ConnectionError:
            pass
    
    expires_at = time.time() + ttl_seconds
    _local_cache[key] = (value, expires_at)


def clear() -> None:
    global _redis_client
    if _redis_client:
        try:
            _redis_client.flushdb()
        except redis.ConnectionError:
            pass
    _local_cache.clear()
