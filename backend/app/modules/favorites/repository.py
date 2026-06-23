from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.favorites.models import Favorite


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, favorite_id: UUID) -> Optional[Favorite]:
        stmt = select(Favorite).where(Favorite.id == favorite_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get(self, user_id: UUID, ebook_id: UUID) -> Optional[Favorite]:
        stmt = (
            select(Favorite)
            .options(joinedload(Favorite.ebook))
            .where(Favorite.user_id == user_id, Favorite.ebook_id == ebook_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID, limit: int = 100, offset: int = 0) -> List[Favorite]:
        stmt = select(Favorite).options(joinedload(Favorite.ebook)).where(
            Favorite.user_id == user_id
        ).order_by(Favorite.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: UUID, ebook_id: UUID) -> Favorite:
        favorite = Favorite(user_id=user_id, ebook_id=ebook_id)
        self.session.add(favorite)
        await self.session.flush()
        stmt = (
            select(Favorite)
            .options(joinedload(Favorite.ebook))
            .where(Favorite.id == favorite.id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, favorite: Favorite) -> None:
        await self.session.delete(favorite)
        await self.session.flush()
