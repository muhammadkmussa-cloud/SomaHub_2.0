from datetime import date, datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.loans.models import Loan


class LoanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, loan_id: UUID, tenant_id: UUID | None = None) -> Optional[Loan]:
        stmt = select(Loan).where(Loan.id == loan_id)
        if tenant_id:
            stmt = stmt.where(Loan.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID | None,
        status: str | None = None,
        borrower_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Loan]:
        stmt = select(Loan)
        if tenant_id:
            stmt = stmt.where(Loan.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Loan.status == status)
        if borrower_id:
            stmt = stmt.where(Loan.borrower_id == borrower_id)
        result = await self.session.execute(
            stmt.order_by(Loan.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def mark_overdue(self, tenant_id: UUID) -> None:
        await self.session.execute(
            update(Loan)
            .where(
                Loan.tenant_id == tenant_id,
                Loan.status == "issued",
                Loan.due_date < date.today(),
            )
            .values(status="overdue", updated_at=datetime.now(timezone.utc))
        )
        await self.session.flush()

    async def create(self, tenant_id: UUID, issued_by_user_id: UUID, **data) -> Loan:
        loan = Loan(tenant_id=tenant_id, issued_by_user_id=issued_by_user_id, **data)
        self.session.add(loan)
        await self.session.flush()
        await self.session.refresh(loan)
        return loan

    async def update_status(self, loan: Loan, status: str) -> Loan:
        loan.status = status
        if status == "returned":
            loan.returned_at = datetime.now(timezone.utc)
        self.session.add(loan)
        await self.session.flush()
        await self.session.refresh(loan)
        return loan
