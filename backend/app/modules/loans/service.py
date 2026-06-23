from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from app.core.exceptions import BorrowerSuspendedError
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.books.repository import BookCopyRepository, BookRepository
from app.modules.borrowers.repository import BorrowerRepository
from app.modules.fines.repository import FineRepository
from app.modules.loans.models import Loan
from app.modules.loans.repository import LoanRepository
from app.modules.loans.schemas import LoanCreate

DAILY_OVERDUE_FINE = Decimal("10.00")
LOST_BOOK_FINE = Decimal("1000.00")


class LoanService:
    def __init__(self, session: AsyncSession):
        self.repo = LoanRepository(session)
        self.borrower_repo = BorrowerRepository(session)
        self.copy_repo = BookCopyRepository(session)
        self.book_repo = BookRepository(session)
        self.fine_repo = FineRepository(session)

    async def get_loan(self, loan_id: UUID, tenant_id: UUID | None = None) -> Loan:
        loan = await self.repo.get(loan_id, tenant_id)
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
        return loan

    async def list_loans(
        self,
        tenant_id: UUID | None,
        status_filter: str | None = None,
        borrower_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Loan]:
        if tenant_id:
            await self.repo.mark_overdue(tenant_id)
        return await self.repo.list(tenant_id, status_filter, borrower_id, limit, offset)

    async def issue_loan(self, tenant_id: UUID, issued_by_user_id: UUID, data: LoanCreate) -> Loan:
        borrower = await self.borrower_repo.get(data.borrower_id, tenant_id)
        if not borrower:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrower not found")
        if borrower.status != "active":
            raise BorrowerSuspendedError()

        copy = await self.copy_repo.get(data.book_copy_id, tenant_id)
        if not copy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book copy not found")
        if copy.status != "available":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Book copy is not available")

        loan = await self.repo.create(tenant_id, issued_by_user_id, **data.model_dump())
        await self.copy_repo.update_status(copy, "loaned")
        book = await self.book_repo.get(copy.book_id, tenant_id)
        if book:
            await self.book_repo.update(book, available_copies=max(0, book.available_copies - 1))
        return loan

    async def return_loan(self, loan_id: UUID, tenant_id: UUID) -> Loan:
        loan = await self.get_loan(loan_id, tenant_id)
        if loan.status not in ["issued", "overdue"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Loan cannot be returned")

        today = date.today()
        if loan.due_date < today:
            overdue_days = (today - loan.due_date).days
            await self.fine_repo.create(
                tenant_id,
                borrower_id=loan.borrower_id,
                loan_id=loan.id,
                reason="overdue",
                amount=DAILY_OVERDUE_FINE * overdue_days,
            )

        copy = await self.copy_repo.get(loan.book_copy_id, tenant_id)
        if copy:
            await self.copy_repo.update_status(copy, "available")
            book = await self.book_repo.get(copy.book_id, tenant_id)
            if book:
                await self.book_repo.update(book, available_copies=min(book.total_copies, book.available_copies + 1))
        return await self.repo.update_status(loan, "returned")

    async def mark_lost(self, loan_id: UUID, tenant_id: UUID) -> Loan:
        loan = await self.get_loan(loan_id, tenant_id)
        if loan.status not in ["issued", "overdue"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Loan cannot be marked lost")
        await self.fine_repo.create(
            tenant_id,
            borrower_id=loan.borrower_id,
            loan_id=loan.id,
            reason="lost_book",
            amount=LOST_BOOK_FINE,
        )
        copy = await self.copy_repo.get(loan.book_copy_id, tenant_id)
        if copy:
            await self.copy_repo.update_status(copy, "lost")
        return await self.repo.update_status(loan, "lost")
