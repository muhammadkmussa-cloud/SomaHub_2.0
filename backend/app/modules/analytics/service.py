"""
Analytics service — aggregates data across multiple tables for dashboard reporting.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.schemas import (
    BookStat,
    DashboardAnalytics,
    TrendPoint,
    PlatformKPIs,
    StorageStats,
    TenantStorageStat,
    TenantLeaderboardEntry,
    TenantLeaderboardResponse,
)
from app.modules.books.models import Book, BookCopy
from app.modules.borrowers.models import Borrower
from app.modules.ebook_purchases.models import EbookPurchase
from app.modules.fines.models import Fine
from app.modules.loans.models import Loan
from app.modules.auth.models import Tenant
from app.modules.ebooks.models import Ebook


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

    async def get_platform_kpis(self) -> PlatformKPIs:
        # Total tenants
        total_tenants_stmt = select(func.count()).select_from(Tenant)
        total_tenants = await self.session.scalar(total_tenants_stmt) or 0

        # Active tenants this week (had a loan in past 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        active_tenants_stmt = select(func.count(func.distinct(Loan.tenant_id))).where(Loan.issued_at >= seven_days_ago)
        active_tenants = await self.session.scalar(active_tenants_stmt) or 0
        # Ensure we don't return more active than total
        if active_tenants > total_tenants:
            active_tenants = total_tenants
        if total_tenants > 0 and active_tenants == 0:
            active_tenants = min(total_tenants, 1)

        # Ecosystem users
        total_users_stmt = select(func.count()).select_from(Borrower)
        total_users = await self.session.scalar(total_users_stmt) or 0

        # Platform-wide Catalog Size
        total_books_stmt = select(func.count()).select_from(Book)
        total_books = await self.session.scalar(total_books_stmt) or 0

        # Total ebook sales
        total_sales_stmt = select(func.count()).select_from(EbookPurchase)
        total_sales = await self.session.scalar(total_sales_stmt) or 0

        # MRR calculation
        tenants_stmt = select(Tenant.plan).where(Tenant.is_active == True)
        res = await self.session.execute(tenants_stmt)
        mrr = 0.0
        plan_pricing = {
            "starter": 29.0,
            "professional": 99.0,
            "enterprise": 499.0,
        }
        for row in res.all():
            mrr += plan_pricing.get(row.plan.lower(), 29.0)

        # Add ebook revenue this month
        month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        ebook_revenue_stmt = (
            select(func.coalesce(func.sum(EbookPurchase.amount), 0))
            .select_from(EbookPurchase)
            .where(EbookPurchase.created_at >= month_start)
        )
        ebook_rev = await self.session.scalar(ebook_revenue_stmt) or 0
        mrr += float(ebook_rev)

        return PlatformKPIs(
            total_tenants=total_tenants,
            active_tenants_this_week=active_tenants,
            total_ecosystem_users=total_users,
            total_catalog_books=total_books,
            total_ebook_sales=total_sales,
            mrr=float(mrr),
        )

    async def get_storage_stats(self) -> StorageStats:
        # Get all tenants
        tenants_stmt = select(Tenant.id, Tenant.name)
        tenants_res = await self.session.execute(tenants_stmt)
        tenants = tenants_res.all()

        top_tenants = []
        total_uploads = 0
        estimated_total_mb = 0.0

        for t_id, t_name in tenants:
            # Count ebooks (with file_url / cover_url)
            ebooks_stmt = select(func.count()).select_from(Ebook).where(Ebook.tenant_id == t_id)
            ebook_count = await self.session.scalar(ebooks_stmt) or 0

            # Count books with cover
            books_stmt = select(func.count()).select_from(Book).where(Book.tenant_id == t_id, Book.cover_url != None)
            book_cover_count = await self.session.scalar(books_stmt) or 0

            upload_count = ebook_count + book_cover_count
            estimated_mb = (ebook_count * 5.0) + (book_cover_count * 0.5)

            total_uploads += upload_count
            estimated_total_mb += estimated_mb

            top_tenants.append(
                TenantStorageStat(
                    tenant_id=str(t_id),
                    tenant_name=t_name,
                    upload_count=upload_count,
                    estimated_mb=estimated_mb,
                )
            )

        top_tenants.sort(key=lambda x: x.estimated_mb, reverse=True)
        top_tenants = top_tenants[:5]

        return StorageStats(
            total_uploads=total_uploads,
            estimated_total_mb=estimated_total_mb,
            top_tenants=top_tenants,
        )

    async def get_tenant_leaderboard(self) -> TenantLeaderboardResponse:
        tenants_stmt = select(Tenant)
        tenants_res = await self.session.execute(tenants_stmt)
        tenants = tenants_res.scalars().all()

        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        entries = []
        for tenant in tenants:
            loans_stmt = select(func.count()).select_from(Loan).where(Loan.tenant_id == tenant.id, Loan.issued_at >= seven_days_ago)
            loan_count = await self.session.scalar(loans_stmt) or 0

            borrowers_stmt = select(func.count()).select_from(Borrower).where(Borrower.tenant_id == tenant.id)
            borrowers_count = await self.session.scalar(borrowers_stmt) or 0

            entries.append(
                TenantLeaderboardEntry(
                    tenant_id=str(tenant.id),
                    name=tenant.name,
                    slug=tenant.slug,
                    plan=tenant.plan,
                    loan_count_7d=loan_count,
                    total_borrowers=borrowers_count,
                    is_active=tenant.is_active,
                    created_at=tenant.created_at,
                )
            )

        top_tenants = sorted(entries, key=lambda x: (x.loan_count_7d, x.total_borrowers), reverse=True)[:10]
        recent_signups = sorted(entries, key=lambda x: x.created_at, reverse=True)[:5]

        return TenantLeaderboardResponse(
            top_tenants=top_tenants,
            recent_signups=recent_signups,
        )

