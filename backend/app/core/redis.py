"""
Redis client for:
  - Refresh token storage and validation
  - JWT blacklist (logout)
  - Rate limiting
  - Temporary tokens (OTP, password reset)
"""

from typing import Optional, Any
import redis.asyncio as aioredis

from app.core.config import settings


class InMemoryMockRedis:
    def __init__(self):
        self._store = {}

    async def setex(self, name: str, time: int, value: str):
        self._store[name] = value

    async def get(self, name: str) -> Optional[str]:
        return self._store.get(name)

    async def delete(self, *names: str):
        for name in names:
            self._store.pop(name, None)

    async def exists(self, name: str) -> int:
        return 1 if name in self._store else 0

    async def ping(self) -> bool:
        return True

    async def aclose(self):
        pass

    class Pipeline:
        def __init__(self, client):
            self.client = client
            self.commands = []

        def incr(self, key: str):
            self.commands.append(("incr", key))

        def expire(self, key: str, seconds: int):
            self.commands.append(("expire", key, seconds))

        async def execute(self) -> list:
            results = []
            for cmd, *args in self.commands:
                if cmd == "incr":
                    key = args[0]
                    current = int(self.client._store.get(key, 0)) + 1
                    self.client._store[key] = str(current)
                    results.append(current)
                elif cmd == "expire":
                    results.append(True)
            self.commands = []
            return results

    def pipeline(self):
        return self.Pipeline(self)


# ── Redis client (module-level singleton) ────────────────────────────────────
_redis: Optional[Any] = None


async def init_redis() -> None:
    """Initialize Redis and test connection."""
    global _redis
    client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )
    try:
        await client.ping()
        _redis = client
    except Exception as exc:
        if settings.APP_ENV in ("development", "testing"):
            import logging

            logging.getLogger(__name__).warning(
                "Redis is not reachable. Falling back to in-memory mock Redis."
            )
            _redis = InMemoryMockRedis()
        else:
            raise RuntimeError(
                f"Redis connection failed in {settings.APP_ENV} environment."
            ) from exc


def get_redis_client() -> Any:
    """Return (or create) the async Redis client."""
    global _redis
    if _redis is None:
        _redis = InMemoryMockRedis()
    return _redis


async def close_redis() -> None:
    """Close the Redis connection pool (called on app shutdown)."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


# ── Key prefixes ──────────────────────────────────────────────────────────────
_REFRESH_PREFIX = "refresh:"
_BLACKLIST_PREFIX = "blacklist:"
_RESET_PREFIX = "reset:"
_VERIFY_PREFIX = "verify:"
_RATE_PREFIX = "rate:"


# ── Refresh token helpers ─────────────────────────────────────────────────────
async def store_refresh_token(user_id: str, token: str, ttl_seconds: int) -> None:
    r = get_redis_client()
    await r.setex(f"{_REFRESH_PREFIX}{user_id}", ttl_seconds, token)


async def get_refresh_token(user_id: str) -> Optional[str]:
    r = get_redis_client()
    return await r.get(f"{_REFRESH_PREFIX}{user_id}")


async def delete_refresh_token(user_id: str) -> None:
    r = get_redis_client()
    await r.delete(f"{_REFRESH_PREFIX}{user_id}")


# ── JWT blacklist helpers ─────────────────────────────────────────────────────
async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    r = get_redis_client()
    await r.setex(f"{_BLACKLIST_PREFIX}{jti}", ttl_seconds, "1")


async def is_token_blacklisted(jti: str) -> bool:
    r = get_redis_client()
    return await r.exists(f"{_BLACKLIST_PREFIX}{jti}") == 1


# ── Short token helpers (password reset, email verify) ───────────────────────
async def store_short_token(
    purpose: str, user_id: str, token: str, ttl_seconds: int
) -> None:
    prefix = _RESET_PREFIX if purpose == "reset" else _VERIFY_PREFIX
    r = get_redis_client()
    await r.setex(f"{prefix}{user_id}", ttl_seconds, token)


async def get_short_token(purpose: str, user_id: str) -> Optional[str]:
    prefix = _RESET_PREFIX if purpose == "reset" else _VERIFY_PREFIX
    r = get_redis_client()
    return await r.get(f"{prefix}{user_id}")


async def delete_short_token(purpose: str, user_id: str) -> None:
    prefix = _RESET_PREFIX if purpose == "reset" else _VERIFY_PREFIX
    r = get_redis_client()
    await r.delete(f"{prefix}{user_id}")


# ── Rate limiting helper ──────────────────────────────────────────────────────
async def increment_rate(key: str, window_seconds: int) -> int:
    """Increment a rate counter and return the new count."""
    r = get_redis_client()
    pipe = r.pipeline()
    pipe.incr(f"{_RATE_PREFIX}{key}")
    pipe.expire(f"{_RATE_PREFIX}{key}", window_seconds)
    results = await pipe.execute()
    return results[0]


async def check_db_connection() -> bool:
    """Health check: verify Redis connectivity."""
    try:
        r = get_redis_client()
        return await r.ping()
    except Exception:
        return False
