from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ebooks.models import Ebook


class EbookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, ebook_id: UUID) -> Optional[Ebook]:
        stmt = select(Ebook).where(Ebook.id == ebook_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        search: str | None = None,
        category: str | None = None,
        status: str | None = "published",  # default to showing only published ebooks
        limit: int = 100,
        offset: int = 0,
    ) -> List[Ebook]:
        stmt = select(Ebook)
        if status:
            stmt = stmt.where(Ebook.status == status)
        if category:
            stmt = stmt.where(Ebook.category == category)
        if search:
            value = f"%{search.strip()}%"
            stmt = stmt.where(or_(Ebook.title.ilike(value), Ebook.author.ilike(value)))

        stmt = stmt.order_by(Ebook.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **data) -> Ebook:
        ebook = Ebook(**data)
        self.session.add(ebook)
        await self.session.flush()
        await self.session.refresh(ebook)
        return ebook

    async def update(self, ebook: Ebook, **data) -> Ebook:
        for key, value in data.items():
            if value is not None:
                setattr(ebook, key, value)
        self.session.add(ebook)
        await self.session.flush()
        await self.session.refresh(ebook)
        return ebook

    async def delete(self, ebook: Ebook) -> None:
        await self.session.delete(ebook)
        await self.session.flush()
