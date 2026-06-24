from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import Tenant
from app.modules.tenants.repository import TenantCRUDRepository
from app.modules.tenants.schemas import TenantCreate, TenantUpdate


class TenantService:
    def __init__(self, session: AsyncSession):
        self.repo = TenantCRUDRepository(session)

    async def get_tenant(self, tenant_id: UUID) -> Tenant:
        tenant = await self.repo.get_by_id(tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
            )
        return tenant

    async def get_tenant_by_slug(self, slug: str) -> Tenant:
        tenant = await self.repo.get_by_slug(slug)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
            )
        return tenant

    async def list_tenants(self, limit: int = 100, offset: int = 0) -> List[Tenant]:
        return await self.repo.get_all(limit, offset)

    async def create_tenant(self, data: TenantCreate) -> Tenant:
        # Check unique constraints
        existing_slug = await self.repo.get_by_slug(data.slug)
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this slug already exists",
            )

        existing_email = await self.repo.get_by_email(data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant with this email already exists",
            )

        return await self.repo.create(
            name=data.name,
            slug=data.slug,
            email=data.email,
            library_type=data.library_type,
            location=data.location,
        )

    async def update_tenant(self, tenant_id: UUID, data: TenantUpdate) -> Tenant:
        tenant = await self.get_tenant(tenant_id)

        if data.slug:
            existing = await self.repo.get_by_slug(data.slug)
            if existing and existing.id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tenant with this slug already exists",
                )

        return await self.repo.update(tenant, **data.model_dump(exclude_unset=True))

    async def delete_tenant(self, tenant_id: UUID) -> None:
        tenant = await self.get_tenant(tenant_id)
        await self.repo.delete(tenant)
