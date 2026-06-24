"""
Test configuration — async fixtures for FastAPI + SQLAlchemy tests.
Uses aiosqlite for isolated test database.
"""

from typing import AsyncGenerator
from uuid import uuid4

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

# Import ALL models so they register on Base.metadata for table creation
from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.main import app as _app

# Model imports — ensures all tables are known to Base.metadata
from app.modules.auth.models import Tenant, User
from app.modules.ebooks.models import Ebook

# ── Test engine ───────────────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ── Override app dependencies ────────────────────────────────────────────────


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_db dependency to use the test database."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


_app.dependency_overrides[get_db] = override_get_db


# ── Test fixtures ─────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> Tenant:
    """Create a test tenant."""
    tenant = Tenant(
        id=uuid4(),
        name="Test Library",
        slug=f"test-library-{uuid4().hex[:8]}",
        email="library@test.com",
        library_type="academic",
        is_active=True,
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test reader user."""
    user = User(
        id=uuid4(),
        tenant_id=test_tenant.id,
        email="reader@test.com",
        username="testreader",
        hashed_password=hash_password("password123"),
        role="reader",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_librarian(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test librarian user."""
    user = User(
        id=uuid4(),
        tenant_id=test_tenant.id,
        email="librarian@test.com",
        username="testlibrarian",
        hashed_password=hash_password("password123"),
        role="librarian",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_library_admin(db_session: AsyncSession, test_tenant: Tenant) -> User:
    """Create a test library admin user."""
    user = User(
        id=uuid4(),
        tenant_id=test_tenant.id,
        email="admin@test.com",
        username="testadmin",
        hashed_password=hash_password("password123"),
        role="library_admin",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ── Auth header fixtures ──────────────────────────────────────────────────────


@pytest_asyncio.fixture
def reader_token(test_user: User) -> str:
    return create_access_token(
        subject=str(test_user.id),
        role=test_user.role,
        tenant_id=str(test_user.tenant_id) if test_user.tenant_id else None,
    )


@pytest_asyncio.fixture
def librarian_token(test_librarian: User) -> str:
    return create_access_token(
        subject=str(test_librarian.id),
        role=test_librarian.role,
        tenant_id=str(test_librarian.tenant_id) if test_librarian.tenant_id else None,
    )


@pytest_asyncio.fixture
def admin_token(test_library_admin: User) -> str:
    return create_access_token(
        subject=str(test_library_admin.id),
        role=test_library_admin.role,
        tenant_id=str(test_library_admin.tenant_id)
        if test_library_admin.tenant_id
        else None,
    )


@pytest_asyncio.fixture
def auth_headers(reader_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {reader_token}"}


@pytest_asyncio.fixture
def librarian_headers(librarian_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {librarian_token}"}


@pytest_asyncio.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


# ── Super admin fixtures ──────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_super_admin(db_session: AsyncSession) -> User:
    """Create a test super admin user (no tenant_id)."""
    user = User(
        id=uuid4(),
        tenant_id=None,
        email="super@admin.com",
        username="superadmin",
        hashed_password=hash_password("password123"),
        role="super_admin",
        is_active=True,
        is_email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def super_admin_token(test_super_admin: User) -> str:
    return create_access_token(
        subject=str(test_super_admin.id),
        role=test_super_admin.role,
        tenant_id=None,
    )


@pytest_asyncio.fixture
def super_admin_headers(super_admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {super_admin_token}"}


# ── Shared ebook fixture ──────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def test_free_ebook(db_session: AsyncSession, test_librarian: User) -> Ebook:
    """Create a free published ebook for digital content tests."""
    ebook = Ebook(
        id=uuid4(),
        tenant_id=test_librarian.tenant_id,
        title="Test Free Ebook",
        author="Test Author",
        description="A free book for testing.",
        category="Test",
        price=0.00,
        status="published",
    )
    db_session.add(ebook)
    await db_session.commit()
    await db_session.refresh(ebook)
    return ebook


# ── Async test client ─────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async test client without auth."""
    transport = httpx.ASGITransport(app=_app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        yield client
