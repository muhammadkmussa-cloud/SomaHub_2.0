from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_role
from app.modules.bookmarks.schemas import BookmarkCreate
from app.modules.bookmarks.service import BookmarkService
from app.modules.favorites.schemas import FavoriteCreate
from app.modules.favorites.service import FavoriteService
from app.modules.reading_progress.schemas import ReadingProgressCreate, ReaderOverviewResponse
from app.modules.reading_progress.service import ReadingProgressService

router = APIRouter(
    prefix="/reader",
    tags=["Reader"],
    dependencies=[Depends(require_role(UserRole.READER))],
)


@router.get("/overview", response_model=ReaderOverviewResponse)
async def get_reader_overview(
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = ReadingProgressService(db)
    return await service.get_reader_overview(user_id=UUID(str(current_user.user_id)))




@router.post("/progress")
async def save_reading_progress(
    ebook_id: UUID = Query(...),
    progress_percent: int = Query(..., ge=0, le=100),
    last_page: int = Query(default=1, ge=1),
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    service = ReadingProgressService(db)
    data = ReadingProgressCreate(
        ebook_id=ebook_id,
        progress_percent=progress_percent,
        last_page=last_page,
    )
    entry = await service.update_progress(user_id=current_user.user_id, data=data)
    return {"success": True, "message": "Progress saved", "data": entry}


@router.get("/progress/{ebook_id}")
async def get_reading_progress(
    ebook_id: UUID,
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    service = ReadingProgressService(db)
    entry = await service.get_progress(user_id=current_user.user_id, ebook_id=ebook_id)
    return {"success": True, "data": entry}


@router.post("/bookmarks")
async def create_bookmark(
    ebook_id: UUID = Query(...),
    page: int = Query(..., ge=1),
    note: str | None = Query(default=None),
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    service = BookmarkService(db)
    data = BookmarkCreate(ebook_id=ebook_id, page=page, note=note)
    bookmark = await service.add_bookmark(user_id=current_user.user_id, data=data)
    return {"success": True, "message": "Bookmark created", "data": bookmark}


@router.get("/bookmarks")
async def list_bookmarks(
    ebook_id: UUID = Query(...),
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    service = BookmarkService(db)
    bookmarks = await service.list_bookmarks(
        user_id=current_user.user_id, ebook_id=ebook_id
    )
    return {"success": True, "data": bookmarks}


@router.post("/favorites")
async def add_favorite(
    ebook_id: UUID = Query(...),
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    service = FavoriteService(db)
    data = FavoriteCreate(ebook_id=ebook_id)
    fav = await service.add_favorite(user_id=current_user.user_id, data=data)
    return {"success": True, "message": "Added to favorites", "data": fav}
