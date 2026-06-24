from typing import List, Optional
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.books.models import Book, BookCopy


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, book_id: UUID, tenant_id: UUID | None = None) -> Optional[Book]:
        stmt = select(Book).where(Book.id == book_id)
        if tenant_id:
            stmt = stmt.where(Book.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID | None = None,
        search: str | None = None,
        author: str | None = None,
        isbn: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Book]:
        stmt: Select[tuple[Book]] = select(Book)
        if tenant_id:
            stmt = stmt.where(Book.tenant_id == tenant_id)
        if search:
            value = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Book.title.ilike(value),
                    Book.author.ilike(value),
                    Book.isbn.ilike(value),
                )
            )
        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author.strip()}%"))
        if isbn:
            stmt = stmt.where(Book.isbn == isbn.strip())
        result = await self.session.execute(
            stmt.order_by(Book.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: UUID, **data) -> Book:
        book = Book(
            tenant_id=tenant_id, available_copies=data.get("total_copies", 0), **data
        )
        self.session.add(book)
        await self.session.flush()
        await self.session.refresh(book)
        return book

    async def update(self, book: Book, **data) -> Book:
        old_total = book.total_copies
        for key, value in data.items():
            if value is not None:
                setattr(book, key, value)
        if "total_copies" in data and data["total_copies"] is not None:
            delta = book.total_copies - old_total
            book.available_copies = max(0, book.available_copies + delta)
        self.session.add(book)
        await self.session.flush()
        await self.session.refresh(book)
        return book

    async def delete(self, book: Book) -> None:
        await self.session.delete(book)
        await self.session.flush()

    async def count_active_loans(
        self, book_id: UUID, tenant_id: UUID | None = None
    ) -> int:
        from app.modules.loans.models import Loan

        stmt = (
            select(func.count())
            .select_from(Loan)
            .join(BookCopy, Loan.book_copy_id == BookCopy.id)
            .where(BookCopy.book_id == book_id, Loan.status.in_(["issued", "overdue"]))
        )
        if tenant_id:
            stmt = stmt.where(Loan.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())


class BookCopyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self, copy_id: UUID, tenant_id: UUID | None = None
    ) -> Optional[BookCopy]:
        stmt = select(BookCopy).where(BookCopy.id == copy_id)
        if tenant_id:
            stmt = stmt.where(BookCopy.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID | None = None,
        book_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[BookCopy]:
        stmt = select(BookCopy)
        if tenant_id:
            stmt = stmt.where(BookCopy.tenant_id == tenant_id)
        if book_id:
            stmt = stmt.where(BookCopy.book_id == book_id)
        if status:
            stmt = stmt.where(BookCopy.status == status)
        result = await self.session.execute(
            stmt.order_by(BookCopy.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: UUID, **data) -> BookCopy:
        copy = BookCopy(tenant_id=tenant_id, **data)
        self.session.add(copy)
        await self.session.flush()
        await self.session.refresh(copy)
        return copy

    async def update_status(self, copy: BookCopy, status: str) -> BookCopy:
        copy.status = status
        self.session.add(copy)
        await self.session.flush()
        await self.session.refresh(copy)
        return copy
