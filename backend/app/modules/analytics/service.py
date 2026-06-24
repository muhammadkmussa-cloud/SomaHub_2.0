"""
Analytics service — aggregates data across multiple tables for dashboard reporting.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.schemas import BookStat, DashboardAnalytics, TrendPoint
from app.modules.books.models import Book, BookCopy
from app.modules.borrowers.models import Borrower
from app.modules.ebook_purchases.models import EbookPurchase
from app.modules.fines.models import Fine
from app.modules.loans.models import Loan


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _tenant_filter(self, model, tenant_id: UUID | None):
        if tenant_id is None:
            return True
        return model.tenant_id == tenant_id

    async def get_dashboard(self, tenant_id: UUID | None = None) -> DashboardAnalytics:
        """Aggregate all key metrics for the analytics dashboard."""
        book_stmt = select(func.count()).select_from(Book)
        borrower_stmt = select(func.count()).select_from(Borrower)
        active_loans_stmt = (
            select(func.count()).select_from(Loan).where(Loan.status == "issued")
        )
        overdue_stmt = (
            select(func.count()).select_from(Loan).where(Loan.status == "overdue")
        )
        fines_stmt = (
            select(func.coalesce(func.sum(Fine.paid_amount), 0))
            .select_from(Fine)
            .where(Fine.status == "paid")
        )

        if tenant_id:
            book_stmt = book_stmt.where(Book.tenant_id == tenant_id)
            borrower_stmt = borrower_stmt.where(Borrower.tenant_id == tenant_id)
            active_loans_stmt = active_loans_stmt.where(Loan.tenant_id == tenant_id)
            overdue_stmt = overdue_stmt.where(Loan.tenant_id == tenant_id)
            fines_stmt = fines_stmt.where(Fine.tenant_id == tenant_id)

        total_books = await self.session.scalar(book_stmt) or 0
        total_borrowers = await self.session.scalar(borrower_stmt) or 0
        active_loans = await self.session.scalar(active_loans_stmt) or 0
        overdue_loans = await self.session.scalar(overdue_stmt) or 0
        total_fines_collected = await self.session.scalar(fines_stmt) or 0

        total_ebook_sales = (
            await self.session.scalar(select(func.count()).select_from(EbookPurchase))
            or 0
        )

        month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        fine_revenue_stmt = (
            select(func.coalesce(func.sum(Fine.paid_amount), 0))
            .select_from(Fine)
            .where(Fine.status == "paid", Fine.paid_at >= month_start)
        )
        if tenant_id:
            fine_revenue_stmt = fine_revenue_stmt.where(Fine.tenant_id == tenant_id)

        ebook_revenue = (
            await self.session.scalar(
                select(func.coalesce(func.sum(EbookPurchase.amount), 0))
                .select_from(EbookPurchase)
                .where(EbookPurchase.created_at >= month_start)
            )
            or 0
        )
        fine_revenue = await self.session.scalar(fine_revenue_stmt) or 0
        revenue_this_month = float(fine_revenue) + float(ebook_revenue)

        top_books = await self._fetch_top_books(tenant_id)

        return DashboardAnalytics(
            total_books=int(total_books),
            total_borrowers=int(total_borrowers),
            active_loans=int(active_loans),
            overdue_loans=int(overdue_loans),
            total_fines_collected=float(total_fines_collected),
            total_ebook_sales=int(total_ebook_sales),
            revenue_this_month=float(revenue_this_month),
            top_books=top_books,
        )

    async def get_trends(
        self, tenant_id: UUID | None = None, days: int = 30
    ) -> list[TrendPoint]:
        """Daily loan counts for the last N days."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        date_col = func.date(Loan.issued_at).label("date")
        stmt = (
            select(date_col, func.count().label("count"))
            .where(Loan.issued_at >= since)
            .group_by(date_col)
            .order_by(date_col)
        )
        if tenant_id:
            stmt = stmt.where(Loan.tenant_id == tenant_id)

        result = await self.session.execute(stmt)
        return [TrendPoint(date=str(row.date), count=row.count) for row in result.all()]

    async def get_top_books(
        self, tenant_id: UUID | None = None, limit: int = 10
    ) -> list[BookStat]:
        return await self._fetch_top_books(tenant_id, limit)

    async def _fetch_top_books(
        self, tenant_id: UUID | None = None, limit: int = 10
    ) -> list[BookStat]:
        stmt = (
            select(
                Book.id,
                Book.title,
                Book.author,
                func.count(Loan.id).label("borrow_count"),
            )
            .join(BookCopy, BookCopy.book_id == Book.id)
            .join(Loan, Loan.book_copy_id == BookCopy.id)
            .group_by(Book.id, Book.title, Book.author)
            .order_by(func.count(Loan.id).desc())
            .limit(limit)
        )
        if tenant_id:
            stmt = stmt.where(Book.tenant_id == tenant_id)

        result = await self.session.execute(stmt)
        return [
            BookStat(
                book_id=str(row.id),
                title=row.title,
                author=row.author,
                borrow_count=row.borrow_count,
            )
            for row in result.all()
        ]
