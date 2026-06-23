"""
Analytics API routes — aggregated library metrics for the dashboard.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.analytics.schemas import DashboardAnalytics, TopBooksResponse, TrendResponse
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
    db: DBSession = None,
):
    """Return aggregated dashboard statistics."""
    service = AnalyticsService(db)
    return await service.get_dashboard(tenant_id=_get_tenant_id(current_user))


@router.get(
    "/trends",
    response_model=TrendResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def get_trends(
    current_user: CurrentUser,
    days: int = 30,
    db: DBSession = None,
):
    """Return daily loan trends for the last N days."""
    service = AnalyticsService(db)
    trends = await service.get_trends(tenant_id=_get_tenant_id(current_user), days=days)
    return TrendResponse(trends=trends)


@router.get(
    "/books",
    response_model=TopBooksResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def get_top_books(
    current_user: CurrentUser,
    limit: int = 10,
    db: DBSession = None,
):
    """Return most borrowed books."""
    service = AnalyticsService(db)
    books = await service.get_top_books(tenant_id=_get_tenant_id(current_user), limit=limit)
    return TopBooksResponse(books=books)
