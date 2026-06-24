from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ebook_purchases.models import EbookPurchase
from app.modules.ebook_purchases.repository import EbookPurchaseRepository
from app.modules.ebook_purchases.schemas import EbookPurchaseCreate


class EbookPurchaseService:
    def __init__(self, session: AsyncSession):
        self.repo = EbookPurchaseRepository(session)

    async def check_ownership(self, user_id: UUID, ebook_id: UUID) -> bool:
        purchase = await self.repo.get_purchase(user_id, ebook_id)
        return purchase is not None

    async def list_user_purchases(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[EbookPurchase]:
        return await self.repo.list_for_user(user_id, limit, offset)

    async def register_purchase(
        self, user_id: UUID, data: EbookPurchaseCreate
    ) -> EbookPurchase:
        # Prevent duplicate purchases
        existing = await self.repo.get_purchase(user_id, data.ebook_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already purchased this ebook",
            )
        return await self.repo.create(user_id, **data.model_dump())
