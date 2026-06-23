from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reviews.models import Review


class ReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, review_id: UUID) -> Optional[Review]:
        stmt = select(Review).where(Review.id == review_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_review(self, user_id: UUID, ebook_id: UUID) -> Optional[Review]:
        stmt = select(Review).where(
            Review.user_id == user_id,
            Review.ebook_id == ebook_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_ebook(self, ebook_id: UUID, limit: int = 50, offset: int = 0) -> List[Review]:
        stmt = select(Review).where(
            Review.ebook_id == ebook_id
        ).order_by(Review.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_id: UUID, **data) -> Review:
        review = Review(user_id=user_id, **data)
        self.session.add(review)
        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def update(self, review: Review, **data) -> Review:
        for key, value in data.items():
            if value is not None:
                setattr(review, key, value)
        self.session.add(review)
        await self.session.flush()
        await self.session.refresh(review)
        return review

    async def delete(self, review: Review) -> None:
        await self.session.delete(review)
        await self.session.flush()
