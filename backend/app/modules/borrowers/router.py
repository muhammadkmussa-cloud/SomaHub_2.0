from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.borrowers.schemas import (
    BorrowerCreate,
    BorrowerResponse,
    BorrowerUpdate,
)
from app.modules.borrowers.service import BorrowerService

router = APIRouter(
    prefix="/borrowers",
    tags=["Borrowers"],
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)


def tenant_scope(current_user: CurrentUser) -> UUID:
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access is required"
        )
    return UUID(current_user.tenant_id)


@router.post("", response_model=BorrowerResponse)
async def create_borrower(
    data: BorrowerCreate, current_user: CurrentUser, db: DBSession = None
):
    service = BorrowerService(db)
    borrower = await service.create_borrower(tenant_scope(current_user), data)
    await db.commit()
    return borrower


@router.get("", response_model=List[BorrowerResponse])
async def list_borrowers(
    current_user: CurrentUser,
    search: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None,
):
    service = BorrowerService(db)
    return await service.list_borrowers(
        tenant_scope(current_user), search, status, limit, offset
    )


@router.get("/{borrower_id}", response_model=BorrowerResponse)
async def get_borrower(
    borrower_id: UUID, current_user: CurrentUser, db: DBSession = None
):
    service = BorrowerService(db)
    return await service.get_borrower(borrower_id, tenant_scope(current_user))


@router.patch("/{borrower_id}", response_model=BorrowerResponse)
async def update_borrower(
    borrower_id: UUID,
    data: BorrowerUpdate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = BorrowerService(db)
    borrower = await service.update_borrower(
        borrower_id, tenant_scope(current_user), data
    )
    await db.commit()
    return borrower


@router.post(
    "/{borrower_id}/suspend",
    response_model=BorrowerResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def suspend_borrower(
    borrower_id: UUID, current_user: CurrentUser, db: DBSession = None
):
    service = BorrowerService(db)
    borrower = await service.suspend_borrower(borrower_id, tenant_scope(current_user))
    await db.commit()
    return borrower
