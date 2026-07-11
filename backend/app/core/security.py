"""
Security utilities: JWT token creation/validation + Argon2 password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────────────────────
_password_hash = PasswordHash([Argon2Hasher()])


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using Argon2."""
    return _password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against an Argon2 hash."""
    return _password_hash.verify(plain_password, hashed_password)


# ── JWT ───────────────────────────────────────────────────────────────────────
def create_access_token(
    subject: str | Any,
    role: str,
    tenant_id: str | None = None,
    session_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire,
    }
    if tenant_id:
        payload["tenant_id"] = str(tenant_id)
    if session_id:
        payload["session_id"] = str(session_id)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | Any,
    role: str,
    tenant_id: str | None = None,
    session_id: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token."""
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "refresh",
        "iat": now,
        "exp": expire,
    }
    if tenant_id:
        payload["tenant_id"] = str(tenant_id)
    if session_id:
        payload["session_id"] = str(session_id)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_short_token(
    subject: str | Any,
    purpose: str,
    expires_minutes: int = 15,
) -> str:
    """Create a short-lived one-time token (password reset, email verify)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "purpose": purpose,
        "type": "short",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError if invalid or expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_short_token",
    "decode_token",
]
