"""
Rate limiting helpers for auth and sensitive endpoints.
"""

from fastapi import Request

from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.core.redis import increment_rate


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def enforce_rate_limit(request: Request, scope: str) -> None:
    """Raise RateLimitExceededError when the client exceeds the configured limit."""
    key = f"{scope}:{_client_ip(request)}"
    count = await increment_rate(key, settings.AUTH_RATE_WINDOW_SECONDS)
    if count > settings.AUTH_RATE_LIMIT:
        raise RateLimitExceededError()
