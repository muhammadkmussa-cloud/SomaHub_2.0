from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.subscriptions.models import Subscription
from app.modules.subscriptions.repository import SubscriptionRepository
from app.modules.subscriptions.schemas import SubscriptionCreate


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.repo = SubscriptionRepository(session)

    async def get_tenant_subscription(self, tenant_id: UUID) -> Subscription:
        sub = await self.repo.get_by_tenant(tenant_id)
        if not sub:
            # Create a default trial subscription
            now = datetime.now(timezone.utc)
            ends = now + timedelta(days=14)  # 14 days free trial
            sub = await self.repo.create(
                tenant_id=tenant_id,
                plan="starter",
                status="trialing",
                starts_at=now,
                ends_at=ends,
            )
        return sub

    async def create_subscription(self, data: SubscriptionCreate) -> Subscription:
        # Check if subscription already exists
        existing = await self.repo.get_by_tenant(data.tenant_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant already has a subscription"
            )
        return await self.repo.create(**data.model_dump())

    async def update_subscription_status(self, tenant_id: UUID, plan: str, status_str: str, days: int = 30) -> Subscription:
        sub = await self.repo.get_by_tenant(tenant_id)
        now = datetime.now(timezone.utc)
        ends = now + timedelta(days=days)
        
        if not sub:
            return await self.repo.create(
                tenant_id=tenant_id,
                plan=plan,
                status=status_str,
                starts_at=now,
                ends_at=ends,
            )
        
        return await self.repo.update(
            sub,
            plan=plan,
            status=status_str,
            starts_at=now,
            ends_at=ends
        )
