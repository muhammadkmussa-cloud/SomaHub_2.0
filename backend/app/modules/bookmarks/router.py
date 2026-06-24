from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DBSession
from app.modules.bookmarks.schemas import BookmarkCreate, BookmarkResponse
from app.modules.bookmarks.service import BookmarkService

router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.get("/ebook/{ebook_id}", response_model=List[BookmarkResponse])
async def list_bookmarks(
    ebook_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = BookmarkService(db)
    return await service.list_bookmarks(UUID(current_user.user_id), ebook_id)


@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    data: BookmarkCreate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = BookmarkService(db)
    bookmark = await service.add_bookmark(UUID(current_user.user_id), data)
    await db.commit()
    return bookmark


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = BookmarkService(db)
    await service.delete_bookmark(UUID(current_user.user_id), bookmark_id)
    await db.commit()
