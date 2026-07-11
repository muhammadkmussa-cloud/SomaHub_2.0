"""
Analytics API routes — aggregated library metrics for the dashboard.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role, require_role
from app.modules.analytics.schemas import (
    DashboardAnalytics,
    TopBooksResponse,
    TrendResponse,
    PlatformKPIs,
    StorageStats,
    TenantLeaderboardResponse,
)
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _get_tenant_id(current_user: CurrentUser) -> UUID | None:
    """Extract tenant_id from the current user, or None for super_admin."""
    if current_user.role == UserRole.SUPER_ADMIN.value:
        return None
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access is required",
        )
    return UUID(current_user.tenant_id)


@router.get(
    "/dashboard",
    response_model=DashboardAnalytics,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def get_dashboard(
    current_user: CurrentUser,
    tenant_id: UUID | None = None,
    db: DBSession = None,
):
    """Return aggregated dashboard statistics."""
    service = AnalyticsService(db)
    t_id = tenant_id if current_user.role == UserRole.SUPER_ADMIN.value else _get_tenant_id(current_user)
    return await service.get_dashboard(tenant_id=t_id)


@router.get(
    "/trends",
    response_model=TrendResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def get_trends(
    current_user: CurrentUser,
    days: int = 30,
    tenant_id: UUID | None = None,
    db: DBSession = None,
):
    """Return daily loan trends for the last N days."""
    service = AnalyticsService(db)
    t_id = tenant_id if current_user.role == UserRole.SUPER_ADMIN.value else _get_tenant_id(current_user)
    trends = await service.get_trends(tenant_id=t_id, days=days)
    return TrendResponse(trends=trends)


@router.get(
    "/books",
    response_model=TopBooksResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def get_top_books(
    current_user: CurrentUser,
    limit: int = 10,
    tenant_id: UUID | None = None,
    db: DBSession = None,
):
    """Return most borrowed books."""
    service = AnalyticsService(db)
    t_id = tenant_id if current_user.role == UserRole.SUPER_ADMIN.value else _get_tenant_id(current_user)
    books = await service.get_top_books(
        tenant_id=t_id, limit=limit
    )
    return TopBooksResponse(books=books)


@router.get(
    "/platform/kpis",
    response_model=PlatformKPIs,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def get_platform_kpis(
    db: DBSession = None,
):
    """Return aggregated platform-wide KPIs (Super Admin only)."""
    service = AnalyticsService(db)
    return await service.get_platform_kpis()


@router.get(
    "/platform/storage",
    response_model=StorageStats,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def get_platform_storage(
    db: DBSession = None,
):
    """Return platform-wide storage statistics (Super Admin only)."""
    service = AnalyticsService(db)
    return await service.get_storage_stats()


@router.get(
    "/platform/leaderboard",
    response_model=TenantLeaderboardResponse,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def get_platform_leaderboard(
    db: DBSession = None,
):
    """Return tenant leaderboard and recent registrations (Super Admin only)."""
    service = AnalyticsService(db)
    return await service.get_tenant_leaderboard()

