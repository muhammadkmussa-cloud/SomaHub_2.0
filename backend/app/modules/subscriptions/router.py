from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.subscriptions.schemas import SubscriptionResponse
from app.modules.subscriptions.service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/status",
    response_model=SubscriptionResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def get_subscription_status(
    current_user: CurrentUser,
    db: DBSession = None,
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant to view subscription status.",
        )
    service = SubscriptionService(db)
    return await service.get_tenant_subscription(UUID(current_user.tenant_id))
