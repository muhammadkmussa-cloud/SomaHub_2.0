from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookmarks.models import Bookmark


class BookmarkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, bookmark_id: UUID) -> Optional[Bookmark]:
        stmt = select(Bookmark).where(Bookmark.id == bookmark_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_ebook(self, user_id: UUID, ebook_id: UUID) -> List[Bookmark]:
        stmt = (
            select(Bookmark)
            .where(Bookmark.user_id == user_id, Bookmark.ebook_id == ebook_id)
            .order_by(Bookmark.page.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: UUID, **data) -> Bookmark:
        bookmark = Bookmark(user_id=user_id, **data)
        self.session.add(bookmark)
        await self.session.flush()
        await self.session.refresh(bookmark)
        return bookmark

    async def delete(self, bookmark: Bookmark) -> None:
        await self.session.delete(bookmark)
        await self.session.flush()
