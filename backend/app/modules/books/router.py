from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.dependencies import CurrentUser, DBSession, require_tenant_write_access
from app.core.permissions import UserRole, require_minimum_role
from app.modules.books.schemas import BookCopyCreate, BookCopyResponse, BookCreate, BookResponse, BookUpdate
from app.modules.books.service import BookService

router = APIRouter(prefix="/books", tags=["Books"])
copy_router = APIRouter(prefix="/book-copies", tags=["Book Copies"])


def tenant_scope(current_user: CurrentUser, write: bool = False) -> UUID | None:
    if current_user.role == UserRole.SUPER_ADMIN.value and not write:
        return None
    if not current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant access is required")
    return UUID(current_user.tenant_id)


@router.post(
    "",
    response_model=BookResponse,
    dependencies=[
        Depends(require_minimum_role(UserRole.LIBRARIAN)),
        Depends(require_tenant_write_access),
    ],
)
async def create_book(data: BookCreate, current_user: CurrentUser, db: DBSession = None):
    service = BookService(db)
    book = await service.create_book(tenant_scope(current_user, write=True), data)
    await db.commit()
    return book


@router.get("", response_model=List[BookResponse])
async def list_books(
    current_user: CurrentUser,
    search: str | None = None,
    author: str | None = None,
    isbn: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None,
):
    service = BookService(db)
    return await service.list_books(tenant_scope(current_user), search, author, isbn, limit, offset)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = BookService(db)
    return await service.get_book(book_id, tenant_scope(current_user))


@router.patch(
    "/{book_id}",
    response_model=BookResponse,
    dependencies=[
        Depends(require_minimum_role(UserRole.LIBRARIAN)),
        Depends(require_tenant_write_access),
    ],
)
async def update_book(book_id: UUID, data: BookUpdate, current_user: CurrentUser, db: DBSession = None):
    service = BookService(db)
    book = await service.update_book(book_id, tenant_scope(current_user, write=True), data)
    await db.commit()
    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_minimum_role(UserRole.LIBRARY_ADMIN)),
        Depends(require_tenant_write_access),
    ],
)
async def delete_book(book_id: UUID, current_user: CurrentUser, db: DBSession = None):
    service = BookService(db)
    await service.delete_book(book_id, tenant_scope(current_user, write=True))
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@copy_router.post(
    "",
    response_model=BookCopyResponse,
    dependencies=[
        Depends(require_minimum_role(UserRole.LIBRARIAN)),
        Depends(require_tenant_write_access),
    ],
)
async def create_copy(data: BookCopyCreate, current_user: CurrentUser, db: DBSession = None):
    service = BookService(db)
    copy = await service.create_copy(tenant_scope(current_user, write=True), data)
    await db.commit()
    return copy


@copy_router.get("", response_model=List[BookCopyResponse], dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))])
async def list_copies(
    current_user: CurrentUser,
    book_id: UUID | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None,
):
    service = BookService(db)
    return await service.list_copies(tenant_scope(current_user), book_id, status, limit, offset)
