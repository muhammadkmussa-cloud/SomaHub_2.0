from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ebook_purchases.repository import EbookPurchaseRepository
from app.modules.reading_progress.models import ReadingProgress
from app.modules.reading_progress.repository import ReadingProgressRepository
from app.modules.reading_progress.schemas import ReadingProgressCreate


class ReadingProgressService:
    def __init__(self, session: AsyncSession):
        self.repo = ReadingProgressRepository(session)
        self.purchase_repo = EbookPurchaseRepository(session)

    async def get_progress(self, user_id: UUID, ebook_id: UUID) -> ReadingProgress:
        # Check ownership or if book is free first
        owned = await self.purchase_repo.get_purchase(user_id, ebook_id)
        if not owned:
            # Check if book is free
            from app.modules.ebooks.repository import EbookRepository
            ebook_repo = EbookRepository(self.repo.session)
            ebook = await ebook_repo.get(ebook_id)
            if not ebook or ebook.price > 0.0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot read ebook without owning it."
                )

        progress = await self.repo.get(user_id, ebook_id)
        if not progress:
            # Create standard initial progress
            progress = await self.repo.update_or_create(user_id, ebook_id, 0, 1)
        return progress

    async def update_progress(self, user_id: UUID, data: ReadingProgressCreate) -> ReadingProgress:
        # Check ownership or if book is free
        owned = await self.purchase_repo.get_purchase(user_id, data.ebook_id)
        if not owned:
            from app.modules.ebooks.repository import EbookRepository
            ebook_repo = EbookRepository(self.repo.session)
            ebook = await ebook_repo.get(data.ebook_id)
            if not ebook or ebook.price > 0.0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot track progress for an unowned priced ebook."
                )

        return await self.repo.update_or_create(
            user_id=user_id,
            ebook_id=data.ebook_id,
            progress_percent=data.progress_percent,
            last_page=data.last_page,
        )
