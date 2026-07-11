from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ebook_purchases.repository import EbookPurchaseRepository
from app.modules.reading_progress.models import ReadingProgress
from app.modules.reading_progress.repository import ReadingProgressRepository
from app.modules.reading_progress.schemas import ReadingProgressCreate


class ReadingProgressService:
    def __init__(self, session: AsyncSession):
        self.repo = ReadingProgressRepository(session)
        self.purchase_repo = EbookPurchaseRepository(session)

    async def get_progress(self, user_id: UUID, ebook_id: UUID) -> ReadingProgress:
        # Check ownership or if book is free first
        owned = await self.purchase_repo.get_purchase(user_id, ebook_id)
        if not owned:
            # Check if book is free
            from app.modules.ebooks.repository import EbookRepository

            ebook_repo = EbookRepository(self.repo.session)
            ebook = await ebook_repo.get(ebook_id)
            if not ebook or ebook.price > 0.0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot read ebook without owning it.",
                )

        progress = await self.repo.get(user_id, ebook_id)
        if not progress:
            # Create standard initial progress
            progress = await self.repo.update_or_create(user_id, ebook_id, 0, 1)
        return progress

    async def update_progress(
        self, user_id: UUID, data: ReadingProgressCreate
    ) -> ReadingProgress:
        # Check ownership or if book is free
        owned = await self.purchase_repo.get_purchase(user_id, data.ebook_id)
        if not owned:
            from app.modules.ebooks.repository import EbookRepository

            ebook_repo = EbookRepository(self.repo.session)
            ebook = await ebook_repo.get(data.ebook_id)
            if not ebook or ebook.price > 0.0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot track progress for an unowned priced ebook.",
                )

        return await self.repo.update_or_create(
            user_id=user_id,
            ebook_id=data.ebook_id,
            progress_percent=data.progress_percent,
            last_page=data.last_page,
        )

    async def get_reader_overview(self, user_id: UUID) -> dict:
        from datetime import datetime, timezone, timedelta
        from sqlalchemy import select, func, extract
        from sqlalchemy.orm import selectinload
        
        # 1. Get last read ebook progress
        stmt_last = (
            select(ReadingProgress)
            .where(ReadingProgress.user_id == user_id)
            .options(selectinload(ReadingProgress.ebook))
            .order_by(ReadingProgress.last_opened_at.desc())
            .limit(1)
        )
        res_last = await self.repo.session.execute(stmt_last)
        last_progress = res_last.scalar_one_or_none()
        
        last_read_data = None
        if last_progress and last_progress.ebook:
            last_read_data = {
                "ebook_id": last_progress.ebook_id,
                "title": last_progress.ebook.title,
                "author": last_progress.ebook.author,
                "cover_url": last_progress.ebook.cover_url,
                "progress_percent": last_progress.progress_percent,
                "last_page": last_progress.last_page,
                "last_opened_at": last_progress.last_opened_at,
            }

        # 2. Get books completed this year
        current_year = datetime.now(timezone.utc).year
        stmt_completed = (
            select(func.count(ReadingProgress.id))
            .where(
                ReadingProgress.user_id == user_id,
                ReadingProgress.progress_percent >= 100,
                extract("year", ReadingProgress.updated_at) == current_year
            )
        )
        res_completed = await self.repo.session.execute(stmt_completed)
        completed_count = res_completed.scalar() or 0

        # 3. Calculate reading streak
        stmt_dates = (
            select(ReadingProgress.last_opened_at)
            .where(ReadingProgress.user_id == user_id)
            .order_by(ReadingProgress.last_opened_at.desc())
        )
        res_dates = await self.repo.session.execute(stmt_dates)
        dates = [row[0].date() for row in res_dates.all() if row[0] is not None]
        unique_dates = sorted(list(set(dates)), reverse=True)
        
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        date_set = set(unique_dates)
        
        streak = 0
        current_date = today
        if current_date in date_set:
            while current_date in date_set:
                streak += 1
                current_date -= timedelta(days=1)
        elif yesterday in date_set:
            current_date = yesterday
            while current_date in date_set:
                streak += 1
                current_date -= timedelta(days=1)
        else:
            streak = 0

        return {
            "last_read": last_read_data,
            "books_completed_this_year": completed_count,
            "reading_goal_this_year": 12,
            "reading_streak_days": streak,
        }

