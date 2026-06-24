"""
FastAPI dependencies for authentication and tenant context.
"""

from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import (
    AuthenticationError,
    InvalidTokenError,
    SubscriptionRequiredError,
    TenantSuspendedError,
)
from app.core.redis import is_token_blacklisted
from app.core.security import decode_token
from app.core.tenant import set_current_tenant_id
from app.modules.auth.repository import TenantRepository
from app.modules.subscriptions.service import SubscriptionService

# Security scheme
_bearer = HTTPBearer(auto_error=False)


# ── Token payload model (lightweight — not a DB call) ─────────────────────────
class TokenPayload:
    def __init__(self, sub: str, role: str, tenant_id: str | None):
        self.user_id = sub
        self.role = role
        self.tenant_id = tenant_id


# ── Current user dependency ───────────────────────────────────────────────────
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> TokenPayload:
    """
    Extract and validate the JWT from the Authorization header.
    Returns a lightweight TokenPayload (no DB hit).
    """
    if credentials is None:
        set_current_tenant_id(None)
        raise AuthenticationError("No authentication token provided.")

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        set_current_tenant_id(None)
        raise InvalidTokenError()

    if payload.get("type") != "access":
        set_current_tenant_id(None)
        raise InvalidTokenError("Invalid token type.")

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        set_current_tenant_id(None)
        raise InvalidTokenError("Token has been revoked.")

    tenant_id_str = payload.get("tenant_id")
    tenant_id = UUID(tenant_id_str) if tenant_id_str else None
    set_current_tenant_id(tenant_id)

    return TokenPayload(
        sub=payload["sub"],
        role=payload.get("role", "reader"),
        tenant_id=tenant_id_str,
    )


# ── Optional current user (for public + authenticated routes) ─────────────────
async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> TokenPayload | None:
    """Like get_current_user but returns None if no token is present."""
    if credentials is None:
        set_current_tenant_id(None)
        return None
    try:
        return await get_current_user(credentials)
    except (AuthenticationError, InvalidTokenError):
        set_current_tenant_id(None)
        return None


# ── Tenant and subscription gates ─────────────────────────────────────────────
async def require_active_tenant(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    if not current_user.tenant_id:
        return
    repo = TenantRepository(db)
    tenant = await repo.get_by_id(UUID(current_user.tenant_id))
    if not tenant or not tenant.is_active:
        raise TenantSuspendedError()


async def require_active_subscription(
    request: Request,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    if not current_user.tenant_id:
        return
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    service = SubscriptionService(db)
    subscription = await service.get_tenant_subscription(UUID(current_user.tenant_id))
    now = datetime.now(timezone.utc)

    if subscription.status == "past_due":
        raise SubscriptionRequiredError(
            "Subscription is past due. Please update billing to continue making changes."
        )

    if subscription.status in ("active", "trialing"):
        ends_at = subscription.ends_at
        if ends_at and ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)
        if ends_at and ends_at <= now:
            raise SubscriptionRequiredError(
                "Subscription has expired. Please renew to continue."
            )
        return

    raise SubscriptionRequiredError(
        "An active subscription is required. Please upgrade your plan to continue."
    )


async def require_tenant_write_access(
    request: Request,
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    await require_active_tenant(current_user, db)
    await require_active_subscription(request, current_user, db)


# ── Type aliases for dependency injection ─────────────────────────────────────
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]
OptionalUser = Annotated[TokenPayload | None, Depends(get_optional_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
ActiveTenant = Annotated[None, Depends(require_active_tenant)]
ActiveSubscription = Annotated[None, Depends(require_active_subscription)]
TenantWriteAccess = Annotated[None, Depends(require_tenant_write_access)]
