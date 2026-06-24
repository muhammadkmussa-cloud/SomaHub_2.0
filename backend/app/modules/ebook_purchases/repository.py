from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.ebook_purchases.models import EbookPurchase


class EbookPurchaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, purchase_id: UUID) -> Optional[EbookPurchase]:
        stmt = select(EbookPurchase).where(EbookPurchase.id == purchase_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_purchase(
        self, user_id: UUID, ebook_id: UUID
    ) -> Optional[EbookPurchase]:
        stmt = (
            select(EbookPurchase)
            .options(joinedload(EbookPurchase.ebook))
            .where(
                EbookPurchase.user_id == user_id,
                EbookPurchase.ebook_id == ebook_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[EbookPurchase]:
        stmt = (
            select(EbookPurchase)
            .options(joinedload(EbookPurchase.ebook))
            .where(EbookPurchase.user_id == user_id)
            .order_by(EbookPurchase.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: UUID, **data) -> EbookPurchase:
        purchase = EbookPurchase(user_id=user_id, **data)
        self.session.add(purchase)
        await self.session.flush()
        stmt = (
            select(EbookPurchase)
            .options(joinedload(EbookPurchase.ebook))
            .where(EbookPurchase.id == purchase.id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
