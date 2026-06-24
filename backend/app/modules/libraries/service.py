from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.libraries.models import Library
from app.modules.libraries.repository import LibraryRepository
from app.modules.libraries.schemas import LibraryUpdate


class LibraryService:
    def __init__(self, session: AsyncSession):
        self.repo = LibraryRepository(session)

    async def get_profile(self, tenant_id: UUID) -> Library:
        profile = await self.repo.get_by_tenant(tenant_id)
        if not profile:
            # Create a default profile if none exists
            profile = await self.repo.create(tenant_id=tenant_id, name="My Library")
        return profile

    async def update_profile(self, tenant_id: UUID, data: LibraryUpdate) -> Library:
        profile = await self.repo.get_by_tenant(tenant_id)
        if not profile:
            profile = await self.repo.create(
                tenant_id=tenant_id, **data.model_dump(exclude_none=True)
            )
        else:
            profile = await self.repo.update(
                profile, **data.model_dump(exclude_none=True)
            )
        return profile
