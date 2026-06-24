from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.plan_limits import enforce_book_limit
from app.modules.books.models import Book, BookCopy
from app.modules.books.repository import BookCopyRepository, BookRepository
from app.modules.books.schemas import BookCopyCreate, BookCreate, BookUpdate


class BookService:
    def __init__(self, session: AsyncSession):
        self.repo = BookRepository(session)
        self.copy_repo = BookCopyRepository(session)

    async def get_book(self, book_id: UUID, tenant_id: UUID | None = None) -> Book:
        book = await self.repo.get(book_id, tenant_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
            )
        return book

    async def list_books(
        self,
        tenant_id: UUID | None = None,
        search: str | None = None,
        author: str | None = None,
        isbn: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Book]:
        return await self.repo.list(tenant_id, search, author, isbn, limit, offset)

    async def create_book(self, tenant_id: UUID, data: BookCreate) -> Book:
        await enforce_book_limit(self.repo.session, tenant_id)
        return await self.repo.create(tenant_id, **data.model_dump())

    async def update_book(
        self, book_id: UUID, tenant_id: UUID, data: BookUpdate
    ) -> Book:
        book = await self.get_book(book_id, tenant_id)
        update_data = data.model_dump(exclude_unset=True)
        if "total_copies" in update_data:
            active_loans = await self.repo.count_active_loans(book.id)
            if update_data["total_copies"] < active_loans:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Total copies cannot be lower than active loans",
                )
        return await self.repo.update(book, **update_data)

    async def delete_book(self, book_id: UUID, tenant_id: UUID) -> None:
        book = await self.get_book(book_id, tenant_id)
        if await self.repo.count_active_loans(book.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Book has active loans"
            )
        await self.repo.delete(book)

    async def create_copy(self, tenant_id: UUID, data: BookCopyCreate) -> BookCopy:
        book = await self.get_book(data.book_id, tenant_id)
        copy = await self.copy_repo.create(tenant_id, **data.model_dump())
        await self.repo.update(book, total_copies=book.total_copies + 1)
        return copy

    async def list_copies(
        self,
        tenant_id: UUID | None = None,
        book_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[BookCopy]:
        return await self.copy_repo.list(tenant_id, book_id, status, limit, offset)
