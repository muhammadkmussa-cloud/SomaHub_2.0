from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.plan_limits import enforce_ebook_limit
from app.modules.ebooks.models import Ebook
from app.modules.ebooks.repository import EbookRepository
from app.modules.ebooks.schemas import EbookCreate, EbookUpdate


class EbookService:
    def __init__(self, session: AsyncSession):
        self.repo = EbookRepository(session)

    async def get_ebook(self, ebook_id: UUID) -> Ebook:
        ebook = await self.repo.get(ebook_id)
        if not ebook:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ebook not found")
        return ebook

    async def list_ebooks(
        self,
        search: str | None = None,
        category: str | None = None,
        status_filter: str | None = "published",
        limit: int = 100,
        offset: int = 0,
    ) -> List[Ebook]:
        return await self.repo.list(search, category, status_filter, limit, offset)

    async def create_ebook(self, tenant_id: UUID | None, data: EbookCreate) -> Ebook:
        if tenant_id is not None:
            await enforce_ebook_limit(self.repo.session, tenant_id)
        payload = data.model_dump()
        if tenant_id is not None:
            payload["tenant_id"] = tenant_id
        return await self.repo.create(**payload)

    async def update_ebook(self, ebook_id: UUID, data: EbookUpdate) -> Ebook:
        ebook = await self.get_ebook(ebook_id)
        return await self.repo.update(ebook, **data.model_dump(exclude_none=True))

    async def delete_ebook(self, ebook_id: UUID) -> None:
        ebook = await self.get_ebook(ebook_id)
        await self.repo.delete(ebook)
