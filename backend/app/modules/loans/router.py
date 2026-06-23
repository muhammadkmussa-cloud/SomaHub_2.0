from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession, require_tenant_write_access
from app.core.permissions import UserRole, require_minimum_role
from app.modules.loans.schemas import LoanCreate, LoanResponse
from app.modules.loans.service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"], dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))])


def tenant_scope(current_user: CurrentUser) -> UUID:
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access is required")
    return UUID(current_user.tenant_id)


@router.post("", response_model=LoanResponse, dependencies=[Depends(require_tenant_write_access)])
async def issue_loan(data: LoanCreate, current_user: CurrentUser, db: DBSession = None):
    service = LoanService(db)
    loan = await service.issue_loan(tenant_scope(current_user), UUID(current_user.user_id), data)
    await db.commit()
    return loan


@router.get("", response_model=List[LoanResponse])
async def list_loans(
    current_user: CurrentUser,
    status: str | None = None,
    borrower_id: UUID | None = None,
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None,
):
    service = LoanService(db)
    loans = await service.list_loans(tenant_scope(current_user), status, borrower_id, limit, offset)
    await db.commit()
    return loans


@router.get("/{loan_id}", response_model=LoanResponse)
async def get_loan(loan_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = LoanService(db)
    return await service.get_loan(loan_id, tenant_scope(current_user))


@router.post("/{loan_id}/return", response_model=LoanResponse, dependencies=[Depends(require_tenant_write_access)])
async def return_loan(loan_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = LoanService(db)
    loan = await service.return_loan(loan_id, tenant_scope(current_user))
    await db.commit()
    return loan


@router.post("/{loan_id}/lost", response_model=LoanResponse)
async def mark_lost(loan_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = LoanService(db)
    loan = await service.mark_lost(loan_id, tenant_scope(current_user))
    await db.commit()
    return loan
