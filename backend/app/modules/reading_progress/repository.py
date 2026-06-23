from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reading_progress.models import ReadingProgress


class ReadingProgressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: UUID, ebook_id: UUID) -> Optional[ReadingProgress]:
        stmt = select(ReadingProgress).where(
            ReadingProgress.user_id == user_id,
            ReadingProgress.ebook_id == ebook_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_or_create(
        self,
        user_id: UUID,
        ebook_id: UUID,
        progress_percent: int,
        last_page: int,
    ) -> ReadingProgress:
        progress = await self.get(user_id, ebook_id)
        now = datetime.now(timezone.utc)
        if progress:
            progress.progress_percent = max(progress.progress_percent, progress_percent)
            progress.last_page = last_page
            progress.last_opened_at = now
        else:
            progress = ReadingProgress(
                user_id=user_id,
                ebook_id=ebook_id,
                progress_percent=progress_percent,
                last_page=last_page,
                last_opened_at=now,
            )
            self.session.add(progress)
            
        await self.session.flush()
        await self.session.refresh(progress)
        return progress
