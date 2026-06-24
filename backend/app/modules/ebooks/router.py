from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.dependencies import CurrentUser, DBSession, OptionalUser
from app.core.permissions import UserRole, has_minimum_role, require_minimum_role
from app.modules.ebooks.schemas import EbookCreate, EbookResponse, EbookUpdate
from app.modules.ebooks.service import EbookService

router = APIRouter(prefix="/ebooks", tags=["Ebooks"])


@router.get("", response_model=List[EbookResponse])
async def list_ebooks(
    search: str | None = None,
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
    current_user: OptionalUser = None,
    db: DBSession = None,
):
    service = EbookService(db)

    # Readers see only published ebooks. Librarians/Admins can see all
    status_filter = "published"
    if current_user and has_minimum_role(current_user.role, UserRole.LIBRARIAN):
        status_filter = None  # Show all statuses (draft, published, archived)

    return await service.list_ebooks(
        search=search,
        category=category,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get("/{ebook_id}", response_model=EbookResponse)
async def get_ebook(
    ebook_id: UUID,
    db: DBSession = None,
):
    service = EbookService(db)
    return await service.get_ebook(ebook_id)


@router.post(
    "",
    response_model=EbookResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def create_ebook(
    data: EbookCreate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = EbookService(db)
    tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
    ebook = await service.create_ebook(tenant_id, data)
    await db.commit()
    return ebook


@router.put(
    "/{ebook_id}",
    response_model=EbookResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def update_ebook(
    ebook_id: UUID,
    data: EbookUpdate,
    db: DBSession = None,
):
    service = EbookService(db)
    ebook = await service.update_ebook(ebook_id, data)
    await db.commit()
    return ebook


@router.delete(
    "/{ebook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def delete_ebook(
    ebook_id: UUID,
    db: DBSession = None,
):
    service = EbookService(db)
    await service.delete_ebook(ebook_id)
    await db.commit()
