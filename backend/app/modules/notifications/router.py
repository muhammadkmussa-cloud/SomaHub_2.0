from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.notifications.schemas import NotificationCreate, NotificationResponse
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
async def list_notifications(
    current_user: CurrentUser,
    status: str | None = None,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: DBSession = None,
):
    service = NotificationService(db)
    tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
    return await service.list_notifications(
        UUID(current_user.user_id), tenant_id, status, category, limit, offset
    )


@router.post(
    "",
    response_model=NotificationResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def create_notification(data: NotificationCreate, db: DBSession = None):
    service = NotificationService(db)
    notification = await service.create_notification(data)
    await db.commit()
    return notification


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID, current_user: CurrentUser, db: DBSession = None
):
    service = NotificationService(db)
    notification = await service.mark_read(notification_id, UUID(current_user.user_id))
    await db.commit()
    return notification
