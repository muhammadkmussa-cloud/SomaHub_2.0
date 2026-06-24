from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ebooks.repository import EbookRepository
from app.modules.favorites.models import Favorite
from app.modules.favorites.repository import FavoriteRepository
from app.modules.favorites.schemas import FavoriteCreate


class FavoriteService:
    def __init__(self, session: AsyncSession):
        self.repo = FavoriteRepository(session)
        self.ebook_repo = EbookRepository(session)

    async def list_favorites(
        self, user_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[Favorite]:
        return await self.repo.list_for_user(user_id, limit, offset)

    async def add_favorite(self, user_id: UUID, data: FavoriteCreate) -> Favorite:
        # Check if ebook exists
        ebook = await self.ebook_repo.get(data.ebook_id)
        if not ebook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Ebook not found"
            )

        # Prevent duplicate favoriting
        existing = await self.repo.get(user_id, data.ebook_id)
        if existing:
            return existing

        return await self.repo.create(user_id, data.ebook_id)

    async def remove_favorite(self, user_id: UUID, ebook_id: UUID) -> None:
        favorite = await self.repo.get(user_id, ebook_id)
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found"
            )
        await self.repo.delete(favorite)
