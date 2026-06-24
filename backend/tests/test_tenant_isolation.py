"""
Tenant isolation and security enforcement tests.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import Tenant
from app.modules.books.models import Book
from app.modules.subscriptions.models import Subscription


@pytest.mark.asyncio
async def test_cross_tenant_book_access_denied(
    async_client,
    db_session: AsyncSession,
    test_tenant,
    test_librarian,
    librarian_headers,
):
    """Tenant B librarian cannot read Tenant A's book by ID."""
    other_tenant = Tenant(
        id=uuid4(),
        name="Other Library",
        slug=f"other-{uuid4().hex[:8]}",
        email="other@test.com",
        library_type="public",
        is_active=True,
    )
    other_book = Book(
        id=uuid4(),
        tenant_id=other_tenant.id,
        title="Private Book",
        author="Other Author",
        total_copies=1,
        available_copies=1,
    )
    db_session.add_all([other_tenant, other_book])
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/books/{other_book.id}",
        headers=librarian_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_reader_cannot_create_book(async_client, auth_headers):
    """Reader role cannot create books."""
    payload = {"title": "Blocked", "author": "Author", "total_copies": 1}
    response = await async_client.post(
        "/api/v1/books", json=payload, headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_suspended_tenant_blocked_on_write(
    async_client,
    db_session: AsyncSession,
    test_tenant,
    test_librarian,
    librarian_headers,
):
    """Suspended tenant cannot create books."""
    test_tenant.is_active = False
    db_session.add(test_tenant)
    await db_session.commit()

    payload = {"title": "Blocked", "author": "Author", "total_copies": 1}
    response = await async_client.post(
        "/api/v1/books", json=payload, headers=librarian_headers
    )
    assert response.status_code == 403
    assert "suspended" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_expired_subscription_blocks_loan(
    async_client,
    db_session: AsyncSession,
    test_tenant,
    test_librarian,
    librarian_headers,
):
    """Canceled subscription blocks loan issuance."""
    sub = Subscription(
        id=uuid4(),
        tenant_id=test_tenant.id,
        plan="starter",
        status="canceled",
        starts_at=datetime.now(timezone.utc) - timedelta(days=30),
        ends_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(sub)
    await db_session.commit()

    response = await async_client.post(
        "/api/v1/loans",
        json={
            "borrower_id": str(uuid4()),
            "book_copy_id": str(uuid4()),
            "due_date": "2030-01-01",
        },
        headers=librarian_headers,
    )
    assert response.status_code == 402


@pytest.mark.asyncio
async def test_super_admin_dashboard_without_tenant(async_client, super_admin_headers):
    """Super admin can access platform-wide analytics."""
    response = await async_client.get(
        "/api/v1/analytics/dashboard",
        headers=super_admin_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_librarian_cannot_access_tenants_list(async_client, librarian_headers):
    """Librarian cannot list all tenants."""
    response = await async_client.get("/api/v1/tenants", headers=librarian_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_past_due_allows_read_blocks_write(
    async_client,
    db_session: AsyncSession,
    test_tenant,
    test_librarian,
    librarian_headers,
):
    """Past-due subscription allows GET but blocks POST."""
    sub = Subscription(
        id=uuid4(),
        tenant_id=test_tenant.id,
        plan="starter",
        status="past_due",
        starts_at=datetime.now(timezone.utc) - timedelta(days=30),
        ends_at=datetime.now(timezone.utc) + timedelta(days=5),
    )
    db_session.add(sub)
    await db_session.commit()

    list_resp = await async_client.get("/api/v1/books", headers=librarian_headers)
    assert list_resp.status_code == 200

    create_resp = await async_client.post(
        "/api/v1/books",
        json={"title": "Blocked", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    assert create_resp.status_code == 402
