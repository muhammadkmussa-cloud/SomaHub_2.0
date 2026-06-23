from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.core.dependencies import DBSession
from app.core.permissions import UserRole, require_role
from app.modules.tenants.schemas import TenantCreate, TenantResponse, TenantUpdate
from app.modules.tenants.service import TenantService

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None
):
    """List all tenants on the platform (Super Admin only)."""
    service = TenantService(db)
    return await service.list_tenants(limit=limit, offset=offset)


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    data: TenantCreate,
    db: DBSession = None
):
    """Create a new tenant (Super Admin only)."""
    service = TenantService(db)
    tenant = await service.create_tenant(data)
    await db.commit()
    return tenant


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    db: DBSession = None
):
    """Retrieve details for a specific tenant (Super Admin only)."""
    service = TenantService(db)
    return await service.get_tenant(tenant_id)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    data: TenantUpdate,
    db: DBSession = None
):
    """Update a tenant's details (Super Admin only)."""
    service = TenantService(db)
    tenant = await service.update_tenant(tenant_id, data)
    await db.commit()
    return tenant


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: UUID,
    db: DBSession = None
):
    """Delete a tenant (Super Admin only)."""
    service = TenantService(db)
    await service.delete_tenant(tenant_id)
    await db.commit()
