from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import NotificationCreate


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.repo = NotificationRepository(session)

    async def list_notifications(
        self,
        user_id: UUID,
        tenant_id: UUID | None = None,
        status_filter: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        return await self.repo.list_for_user(
            user_id, tenant_id, status_filter, category, limit, offset
        )

    async def create_notification(self, data: NotificationCreate) -> Notification:
        return await self.repo.create(**data.model_dump())

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notification = await self.repo.get(notification_id, user_id)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        return await self.repo.mark_read(notification)
