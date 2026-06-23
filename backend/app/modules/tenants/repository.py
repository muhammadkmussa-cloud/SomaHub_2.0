from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import Tenant

class TenantCRUDRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tenant_id: UUID) -> Optional[Tenant]:
        result = await self.session.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        result = await self.session.execute(
            select(Tenant).where(Tenant.slug == slug.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Tenant]:
        result = await self.session.execute(
            select(Tenant).where(Tenant.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Tenant]:
        result = await self.session.execute(
            select(Tenant).offset(offset).limit(limit).order_by(Tenant.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, name: str, slug: str, email: str, library_type: Optional[str] = None, location: Optional[str] = None) -> Tenant:
        tenant = Tenant(
            name=name,
            slug=slug.lower().strip(),
            email=email.lower().strip(),
            library_type=library_type,
            location=location,
        )
        self.session.add(tenant)
        await self.session.flush()
        await self.session.refresh(tenant)
        return tenant

    async def update(self, tenant: Tenant, **kwargs) -> Tenant:
        for key, value in kwargs.items():
            if value is not None:
                if key == "slug" or key == "email":
                    value = value.lower().strip()
                setattr(tenant, key, value)
        self.session.add(tenant)
        await self.session.flush()
        await self.session.refresh(tenant)
        return tenant

    async def delete(self, tenant: Tenant) -> None:
        await self.session.delete(tenant)
        await self.session.flush()
