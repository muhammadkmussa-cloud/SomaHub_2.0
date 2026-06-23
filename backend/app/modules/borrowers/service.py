from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.borrowers.models import Borrower
from app.modules.borrowers.repository import BorrowerRepository
from app.modules.borrowers.schemas import BorrowerCreate, BorrowerUpdate


class BorrowerService:
    def __init__(self, session: AsyncSession):
        self.repo = BorrowerRepository(session)

    async def get_borrower(self, borrower_id: UUID, tenant_id: UUID | None = None) -> Borrower:
        borrower = await self.repo.get(borrower_id, tenant_id)
        if not borrower:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrower not found")
        return borrower

    async def list_borrowers(
        self,
        tenant_id: UUID | None,
        search: str | None = None,
        status_filter: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Borrower]:
        return await self.repo.list(tenant_id, search, status_filter, limit, offset)

    async def create_borrower(self, tenant_id: UUID, data: BorrowerCreate) -> Borrower:
        return await self.repo.create(tenant_id, **data.model_dump())

    async def update_borrower(self, borrower_id: UUID, tenant_id: UUID, data: BorrowerUpdate) -> Borrower:
        borrower = await self.get_borrower(borrower_id, tenant_id)
        return await self.repo.update(borrower, **data.model_dump(exclude_unset=True))

    async def suspend_borrower(self, borrower_id: UUID, tenant_id: UUID) -> Borrower:
        borrower = await self.get_borrower(borrower_id, tenant_id)
        return await self.repo.update(borrower, status="suspended")
