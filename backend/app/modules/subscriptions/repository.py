from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.subscriptions.models import Subscription


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, subscription_id: UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.id == subscription_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: UUID) -> Optional[Subscription]:
        stmt = select(Subscription).where(Subscription.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, **data) -> Subscription:
        subscription = Subscription(**data)
        self.session.add(subscription)
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription

    async def update(self, subscription: Subscription, **data) -> Subscription:
        for key, value in data.items():
            if value is not None:
                setattr(subscription, key, value)
        self.session.add(subscription)
        await self.session.flush()
        await self.session.refresh(subscription)
        return subscription
