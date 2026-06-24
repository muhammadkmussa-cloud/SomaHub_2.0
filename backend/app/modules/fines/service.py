from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.borrowers.repository import BorrowerRepository
from app.modules.fines.models import Fine
from app.modules.fines.repository import FineRepository
from app.modules.fines.schemas import FineCreate


class FineService:
    def __init__(self, session: AsyncSession):
        self.repo = FineRepository(session)
        self.borrower_repo = BorrowerRepository(session)

    async def get_fine(self, fine_id: UUID, tenant_id: UUID | None = None) -> Fine:
        fine = await self.repo.get(fine_id, tenant_id)
        if not fine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fine not found"
            )
        return fine

    async def list_fines(
        self,
        tenant_id: UUID | None = None,
        status_filter: str | None = None,
        borrower_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Fine]:
        return await self.repo.list(
            tenant_id, status_filter, borrower_id, limit, offset
        )

    async def create_fine(self, tenant_id: UUID, data: FineCreate) -> Fine:
        borrower = await self.borrower_repo.get(data.borrower_id, tenant_id)
        if not borrower:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Borrower not found"
            )
        return await self.repo.create(tenant_id, **data.model_dump())

    async def pay_fine(self, fine_id: UUID, tenant_id: UUID, amount: Decimal) -> Fine:
        fine = await self.get_fine(fine_id, tenant_id)
        if fine.status != "unpaid":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Fine is not payable"
            )
        if fine.paid_amount + amount > fine.amount:
            amount = fine.amount - fine.paid_amount
        return await self.repo.pay(fine, amount)

    async def waive_fine(self, fine_id: UUID, tenant_id: UUID) -> Fine:
        fine = await self.get_fine(fine_id, tenant_id)
        if fine.status == "paid":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Paid fines cannot be waived",
            )
        return await self.repo.waive(fine)
