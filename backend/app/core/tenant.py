import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable to hold the current tenant ID for the duration of a request
_tenant_id_ctx: ContextVar[Optional[uuid.UUID]] = ContextVar("tenant_id", default=None)


def get_current_tenant_id() -> Optional[uuid.UUID]:
    """Retrieve the current tenant ID from the context."""
    return _tenant_id_ctx.get()


def set_current_tenant_id(tenant_id: Optional[uuid.UUID]) -> None:
    """Set the current tenant ID in the context."""
    _tenant_id_ctx.set(tenant_id)


def clear_current_tenant_id() -> None:
    """Clear the tenant ID from the context."""
    _tenant_id_ctx.set(None)
