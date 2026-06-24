from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self, notification_id: UUID, user_id: UUID | None = None
    ) -> Optional[Notification]:
        stmt = select(Notification).where(Notification.id == notification_id)
        if user_id:
            stmt = stmt.where(Notification.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: UUID,
        tenant_id: UUID | None = None,
        status: str | None = None,
        category: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if tenant_id is not None:
            stmt = stmt.where(Notification.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Notification.status == status)
        if category:
            stmt = stmt.where(Notification.category == category)
        result = await self.session.execute(
            stmt.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **data) -> Notification:
        notification = Notification(**data)
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification

    async def mark_read(self, notification: Notification) -> Notification:
        notification.status = "read"
        notification.read_at = datetime.now(timezone.utc)
        self.session.add(notification)
        await self.session.flush()
        await self.session.refresh(notification)
        return notification
