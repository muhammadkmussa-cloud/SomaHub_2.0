"""Plan limit enforcement tests."""

import pytest
from uuid import uuid4

from app.core import subscription as subscription_module
from app.core.exceptions import SubscriptionRequiredError
from app.core.plan_limits import enforce_ebook_limit, enforce_user_limit
from app.core.security import hash_password
from app.modules.auth.models import User
from app.modules.ebooks.models import Ebook


@pytest.mark.asyncio
async def test_book_limit_enforced(async_client, test_librarian, librarian_headers, monkeypatch):
    """POST /api/v1/books → 402 when tenant exceeds plan book limit."""
    monkeypatch.setitem(subscription_module.PLAN_LIMITS["starter"], "max_books", 1)

    payload = {"title": "First Book", "author": "Author One", "total_copies": 1}
    first = await async_client.post("/api/v1/books", json=payload, headers=librarian_headers)
    assert first.status_code == 200

    second_payload = {"title": "Second Book", "author": "Author Two", "total_copies": 1}
    second = await async_client.post("/api/v1/books", json=second_payload, headers=librarian_headers)
    assert second.status_code == 402
    assert "Book limit reached" in second.json()["message"]


@pytest.mark.asyncio
async def test_ebook_limit_enforced(async_client, librarian_headers, monkeypatch):
    """POST /api/v1/ebooks → 402 when tenant exceeds plan ebook limit."""
    monkeypatch.setitem(subscription_module.PLAN_LIMITS["starter"], "max_ebooks", 1)

    first = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Ebook One", "author": "Author", "price": 0},
        headers=librarian_headers,
    )
    assert first.status_code == 201

    second = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Ebook Two", "author": "Author", "price": 0},
        headers=librarian_headers,
    )
    assert second.status_code == 402
    assert "Ebook limit reached" in second.json()["message"]


@pytest.mark.asyncio
async def test_user_limit_helper(db_session, test_tenant, monkeypatch):
    """enforce_user_limit raises when tenant is at capacity."""
    monkeypatch.setitem(subscription_module.PLAN_LIMITS["starter"], "max_users", 1)

    db_session.add(
        User(
            id=uuid4(),
            tenant_id=test_tenant.id,
            email="staff@test.com",
            username="staff",
            hashed_password=hash_password("password123"),
            role="librarian",
            is_active=True,
            is_email_verified=True,
        )
    )
    await db_session.commit()

    with pytest.raises(SubscriptionRequiredError, match="User limit reached"):
        await enforce_user_limit(db_session, test_tenant.id)


@pytest.mark.asyncio
async def test_ebook_limit_helper(db_session, test_tenant, monkeypatch):
    """enforce_ebook_limit raises when tenant is at capacity."""
    monkeypatch.setitem(subscription_module.PLAN_LIMITS["starter"], "max_ebooks", 1)

    db_session.add(
        Ebook(
            id=uuid4(),
            tenant_id=test_tenant.id,
            title="Existing",
            author="Author",
            price=0,
            status="published",
        )
    )
    await db_session.commit()

    with pytest.raises(SubscriptionRequiredError, match="Ebook limit reached"):
        await enforce_ebook_limit(db_session, test_tenant.id)
