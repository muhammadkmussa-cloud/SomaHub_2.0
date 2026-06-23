"""
Role-Based Access Control (RBAC) permission system.
Defines roles and provides FastAPI dependency factories for role enforcement.
"""

from enum import StrEnum
from typing import Callable

from fastapi import Depends

from app.core.exceptions import PermissionDeniedError


# ── Role definitions ──────────────────────────────────────────────────────────
class UserRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    LIBRARY_ADMIN = "library_admin"
    LIBRARIAN = "librarian"
    READER = "reader"


# ── Role hierarchy ────────────────────────────────────────────────────────────
# Higher index = higher privilege level
ROLE_HIERARCHY: list[UserRole] = [
    UserRole.READER,
    UserRole.LIBRARIAN,
    UserRole.LIBRARY_ADMIN,
    UserRole.SUPER_ADMIN,
]


def role_level(role: UserRole | str) -> int:
    """Return the numeric privilege level for a given role."""
    try:
        return ROLE_HIERARCHY.index(UserRole(role))
    except ValueError:
        return -1


def has_minimum_role(user_role: str, required_role: UserRole) -> bool:
    """Check if user_role meets or exceeds required_role."""
    return role_level(user_role) >= role_level(required_role)


# ── Dependency factories ──────────────────────────────────────────────────────
def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Factory that returns a FastAPI dependency enforcing one of the allowed roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
    """
    from app.core.dependencies import get_current_user  # avoid circular import

    async def _check(current_user=Depends(get_current_user)) -> None:
        if current_user.role not in [r.value for r in allowed_roles]:
            raise PermissionDeniedError()

    return _check


def require_minimum_role(minimum_role: UserRole) -> Callable:
    """
    Factory that returns a FastAPI dependency enforcing minimum role level.

    Usage:
        @router.get("/lib", dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))])
    """
    from app.core.dependencies import get_current_user  # avoid circular import

    async def _check(current_user=Depends(get_current_user)) -> None:
        if not has_minimum_role(current_user.role, minimum_role):
            raise PermissionDeniedError()

    return _check


__all__ = [
    "UserRole",
    "ROLE_HIERARCHY",
    "role_level",
    "has_minimum_role",
    "require_role",
    "require_minimum_role",
]
