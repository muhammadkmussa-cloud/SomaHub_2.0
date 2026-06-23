#!/usr/bin/env python3
"""Seed deterministic data for Playwright E2E tests."""

import asyncio
import os
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

os.environ.setdefault("APP_ENV", "testing")

from app.core.database import Base
from app.core.security import hash_password
from app.modules.auth.models import Tenant, User
from app.modules.books.models import Book, BookCopy  # noqa: F401
from app.modules.borrowers.models import Borrower  # noqa: F401
from app.modules.loans.models import Loan  # noqa: F401
from app.modules.fines.models import Fine  # noqa: F401
from app.modules.ebooks.models import Ebook  # noqa: F401
from app.modules.ebook_purchases.models import EbookPurchase  # noqa: F401
from app.modules.notifications.models import Notification  # noqa: F401
from app.modules.payments.models import Payment  # noqa: F401
from app.modules.subscriptions.models import Subscription  # noqa: F401
from app.modules.reading_progress.models import ReadingProgress  # noqa: F401
from app.modules.bookmarks.models import Bookmark  # noqa: F401
from app.modules.favorites.models import Favorite  # noqa: F401
from app.modules.reviews.models import Review  # noqa: F401
from app.modules.libraries.models import Library  # noqa: F401

E2E_LIBRARIAN_EMAIL = "e2e-librarian@test.com"
E2E_PASSWORD = "password123"


async def seed() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./e2e.db")
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    poolclass = StaticPool if database_url.startswith("sqlite") else None

    engine = create_async_engine(
        database_url,
        connect_args=connect_args,
        poolclass=poolclass,
    )
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        tenant = Tenant(
            id=uuid4(),
            name="E2E Library",
            slug="e2e-library",
            email="e2e-library@test.com",
            library_type="public",
            is_active=True,
        )
        session.add(tenant)
        await session.flush()

        librarian = User(
            id=uuid4(),
            tenant_id=tenant.id,
            email=E2E_LIBRARIAN_EMAIL,
            username="e2elibrarian",
            hashed_password=hash_password(E2E_PASSWORD),
            role="librarian",
            is_active=True,
            is_email_verified=True,
        )
        session.add(librarian)
        await session.commit()

    await engine.dispose()
    print(f"E2E seed complete: {E2E_LIBRARIAN_EMAIL} / {E2E_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
