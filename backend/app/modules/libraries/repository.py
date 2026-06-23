from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.libraries.models import Library


class LibraryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_tenant(self, tenant_id: UUID) -> Optional[Library]:
        stmt = select(Library).where(Library.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, tenant_id: UUID, **data) -> Library:
        library = Library(tenant_id=tenant_id, **data)
        self.session.add(library)
        await self.session.flush()
        await self.session.refresh(library)
        return library

    async def update(self, library: Library, **data) -> Library:
        for key, value in data.items():
            if value is not None:
                setattr(library, key, value)
        self.session.add(library)
        await self.session.flush()
        await self.session.refresh(library)
        return library
