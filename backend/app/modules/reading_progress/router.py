from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DBSession
from app.modules.reading_progress.schemas import (
    ReadingProgressCreate,
    ReadingProgressResponse,
)
from app.modules.reading_progress.service import ReadingProgressService

router = APIRouter(prefix="/reading-progress", tags=["Reading Progress"])


@router.get("/{ebook_id}", response_model=ReadingProgressResponse)
async def get_progress(
    ebook_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = ReadingProgressService(db)
    return await service.get_progress(UUID(current_user.user_id), ebook_id)


@router.post("", response_model=ReadingProgressResponse)
async def update_progress(
    data: ReadingProgressCreate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = ReadingProgressService(db)
    progress = await service.update_progress(UUID(current_user.user_id), data)
    await db.commit()
    return progress
