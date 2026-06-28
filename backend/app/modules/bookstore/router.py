from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_role
from app.modules.ebooks.schemas import EbookResponse
from app.modules.ebooks.service import EbookService

router = APIRouter(
    prefix="/bookstore",
    tags=["Bookstore"],
    dependencies=[Depends(require_role(UserRole.READER, UserRole.SUPER_ADMIN))],
)


@router.get("/ebooks")
async def browse_ebooks(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
):
    service = EbookService(db)
    ebooks = await service.list_ebooks(
        search=search,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    return {
        "success": True,
        "data": [EbookResponse.model_validate(e) for e in ebooks],
        "page": page,
        "page_size": page_size,
    }


@router.get("/ebooks/{ebook_id}")
async def get_ebook_details(
    ebook_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    service = EbookService(db)
    try:
        ebook = await service.get_ebook(ebook_id)
    except HTTPException:
        raise
    return {"success": True, "data": EbookResponse.model_validate(ebook)}


@router.get("/my-library")
async def my_library(
    current_user: CurrentUser,
    db: DBSession,
):
    from app.modules.ebook_purchases.service import EbookPurchaseService

    service = EbookPurchaseService(db)
    purchases = await service.list_user_purchases(current_user.user_id)
    return {"success": True, "data": purchases}
