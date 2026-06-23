from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DBSession
from app.modules.favorites.schemas import FavoriteCreate, FavoriteResponse
from app.modules.favorites.service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("", response_model=List[FavoriteResponse])
async def list_favorites(
    limit: int = 100,
    offset: int = 0,
    current_user: CurrentUser = None,
    db: DBSession = None,
):
    service = FavoriteService(db)
    return await service.list_favorites(UUID(current_user.user_id), limit, offset)


@router.post("", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    data: FavoriteCreate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = FavoriteService(db)
    favorite = await service.add_favorite(UUID(current_user.user_id), data)
    await db.commit()
    return favorite


@router.delete("/{ebook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    ebook_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = FavoriteService(db)
    await service.remove_favorite(UUID(current_user.user_id), ebook_id)
    await db.commit()
