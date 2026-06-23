from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ebook_purchases.repository import EbookPurchaseRepository
from app.modules.ebooks.repository import EbookRepository
from app.modules.reviews.models import Review
from app.modules.reviews.repository import ReviewRepository
from app.modules.reviews.schemas import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, session: AsyncSession):
        self.repo = ReviewRepository(session)
        self.purchase_repo = EbookPurchaseRepository(session)
        self.ebook_repo = EbookRepository(session)

    async def list_reviews(self, ebook_id: UUID, limit: int = 50, offset: int = 0) -> List[Review]:
        return await self.repo.list_for_ebook(ebook_id, limit, offset)

    async def add_review(self, user_id: UUID, data: ReviewCreate) -> Review:
        # Check if ebook exists
        ebook = await self.ebook_repo.get(data.ebook_id)
        if not ebook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ebook not found"
            )

        # Ensure user purchased the ebook before reviewing
        owned = await self.purchase_repo.get_purchase(user_id, data.ebook_id)
        if not owned and ebook.price > 0.0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must purchase this ebook before reviewing it."
            )

        # Prevent duplicate reviews
        existing = await self.repo.get_user_review(user_id, data.ebook_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this ebook. You can update your existing review."
            )

        return await self.repo.create(user_id, **data.model_dump())

    async def update_review(self, user_id: UUID, review_id: UUID, data: ReviewUpdate) -> Review:
        review = await self.repo.get(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot edit someone else's review"
            )
        return await self.repo.update(review, **data.model_dump(exclude_none=True))

    async def delete_review(self, user_id: UUID, review_id: UUID) -> None:
        review = await self.repo.get(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete someone else's review"
            )
        await self.repo.delete(review)
