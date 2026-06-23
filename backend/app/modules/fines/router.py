from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.fines.schemas import FineCreate, FinePayment, FineResponse
from app.modules.fines.service import FineService

router = APIRouter(prefix="/fines", tags=["Fines"], dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))])


def tenant_scope(current_user: CurrentUser) -> UUID:
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access is required")
    return UUID(current_user.tenant_id)


@router.post("", response_model=FineResponse)
async def create_fine(data: FineCreate, current_user: CurrentUser, db: DBSession = None):
    service = FineService(db)
    fine = await service.create_fine(tenant_scope(current_user), data)
    await db.commit()
    return fine


@router.get("", response_model=List[FineResponse])
async def list_fines(
    current_user: CurrentUser,
    status: str | None = None,
    borrower_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None,
):
    service = FineService(db)
    return await service.list_fines(tenant_scope(current_user), status, borrower_id, limit, offset)


@router.get("/{fine_id}", response_model=FineResponse)
async def get_fine(fine_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = FineService(db)
    return await service.get_fine(fine_id, tenant_scope(current_user))


@router.post("/{fine_id}/pay", response_model=FineResponse)
async def pay_fine(fine_id: UUID, data: FinePayment, current_user: CurrentUser, db: DBSession = None):
    service = FineService(db)
    fine = await service.pay_fine(fine_id, tenant_scope(current_user), data.amount)
    await db.commit()
    return fine


@router.post("/{fine_id}/waive", response_model=FineResponse, dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))])
async def waive_fine(fine_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = FineService(db)
    fine = await service.waive_fine(fine_id, tenant_scope(current_user))
    await db.commit()
    return fine
