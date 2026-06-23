from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DBSession
from app.modules.reviews.schemas import ReviewCreate, ReviewResponse, ReviewUpdate
from app.modules.reviews.service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/ebook/{ebook_id}", response_model=List[ReviewResponse])
async def list_reviews(
    ebook_id: UUID,
    limit: int = 50,
    offset: int = 0,
    db: DBSession = None,
):
    service = ReviewService(db)
    return await service.list_reviews(ebook_id, limit, offset)


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(
    data: ReviewCreate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = ReviewService(db)
    review = await service.add_review(UUID(current_user.user_id), data)
    await db.commit()
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = ReviewService(db)
    review = await service.update_review(UUID(current_user.user_id), review_id, data)
    await db.commit()
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = ReviewService(db)
    await service.delete_review(UUID(current_user.user_id), review_id)
    await db.commit()
