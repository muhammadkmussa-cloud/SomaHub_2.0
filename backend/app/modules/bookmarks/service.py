from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookmarks.models import Bookmark
from app.modules.bookmarks.repository import BookmarkRepository
from app.modules.bookmarks.schemas import BookmarkCreate
from app.modules.ebook_purchases.repository import EbookPurchaseRepository


class BookmarkService:
    def __init__(self, session: AsyncSession):
        self.repo = BookmarkRepository(session)
        self.purchase_repo = EbookPurchaseRepository(session)

    async def list_bookmarks(self, user_id: UUID, ebook_id: UUID) -> List[Bookmark]:
        # Check ownership or if book is free
        owned = await self.purchase_repo.get_purchase(user_id, ebook_id)
        if not owned:
            from app.modules.ebooks.repository import EbookRepository

            ebook_repo = EbookRepository(self.repo.session)
            ebook = await ebook_repo.get(ebook_id)
            if not ebook or ebook.price > 0.0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view bookmarks for an unowned ebook.",
                )

        return await self.repo.list_for_ebook(user_id, ebook_id)

    async def add_bookmark(self, user_id: UUID, data: BookmarkCreate) -> Bookmark:
        # Check ownership or if book is free
        owned = await self.purchase_repo.get_purchase(user_id, data.ebook_id)
        if not owned:
            from app.modules.ebooks.repository import EbookRepository

            ebook_repo = EbookRepository(self.repo.session)
            ebook = await ebook_repo.get(data.ebook_id)
            if not ebook or ebook.price > 0.0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot bookmark an unowned ebook.",
                )

        return await self.repo.create(user_id, **data.model_dump())

    async def delete_bookmark(self, user_id: UUID, bookmark_id: UUID) -> None:
        bookmark = await self.repo.get(bookmark_id)
        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found"
            )
        if bookmark.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete someone else's bookmark",
            )
        await self.repo.delete(bookmark)
