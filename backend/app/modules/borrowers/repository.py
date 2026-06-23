from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.borrowers.models import Borrower


class BorrowerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, borrower_id: UUID, tenant_id: UUID | None = None) -> Optional[Borrower]:
        stmt = select(Borrower).where(Borrower.id == borrower_id)
        if tenant_id:
            stmt = stmt.where(Borrower.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID | None,
        search: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Borrower]:
        stmt = select(Borrower)
        if tenant_id:
            stmt = stmt.where(Borrower.tenant_id == tenant_id)
        if search:
            value = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Borrower.first_name.ilike(value),
                    Borrower.last_name.ilike(value),
                    Borrower.email.ilike(value),
                    Borrower.student_id.ilike(value),
                )
            )
        if status:
            stmt = stmt.where(Borrower.status == status)
        result = await self.session.execute(stmt.order_by(Borrower.created_at.desc()).offset(offset).limit(limit))
        return list(result.scalars().all())

    async def create(self, tenant_id: UUID, **data) -> Borrower:
        borrower = Borrower(tenant_id=tenant_id, **data)
        self.session.add(borrower)
        await self.session.flush()
        await self.session.refresh(borrower)
        return borrower

    async def update(self, borrower: Borrower, **data) -> Borrower:
        for key, value in data.items():
            if value is not None:
                setattr(borrower, key, value)
        self.session.add(borrower)
        await self.session.flush()
        await self.session.refresh(borrower)
        return borrower
