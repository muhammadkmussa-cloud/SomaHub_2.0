"""Subscription plan limit enforcement helpers."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import SubscriptionRequiredError
from app.core.subscription import get_plan_limits
from app.modules.auth.models import User
from app.modules.books.models import Book
from app.modules.ebooks.models import Ebook
from app.modules.subscriptions.service import SubscriptionService


async def _get_limits(session: AsyncSession, tenant_id: UUID):
    sub_service = SubscriptionService(session)
    subscription = await sub_service.get_tenant_subscription(tenant_id)
    return get_plan_limits(subscription.plan)


async def enforce_book_limit(session: AsyncSession, tenant_id: UUID) -> None:
    """Raise if tenant has reached max books for their subscription plan."""
    limits = await _get_limits(session, tenant_id)
    count = await session.scalar(
        select(func.count()).select_from(Book).where(Book.tenant_id == tenant_id)
    )
    if (count or 0) >= limits["max_books"]:
        raise SubscriptionRequiredError(
            f"Book limit reached ({limits['max_books']}). Upgrade your plan to add more books."
        )


async def enforce_user_limit(session: AsyncSession, tenant_id: UUID) -> None:
    """Raise if tenant has reached max staff users for their subscription plan."""
    limits = await _get_limits(session, tenant_id)
    count = await session.scalar(
        select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
    )
    if (count or 0) >= limits["max_users"]:
        raise SubscriptionRequiredError(
            f"User limit reached ({limits['max_users']}). Upgrade your plan to add more users."
        )


async def enforce_ebook_limit(session: AsyncSession, tenant_id: UUID) -> None:
    """Raise if tenant has reached max ebooks for their subscription plan."""
    limits = await _get_limits(session, tenant_id)
    count = await session.scalar(
        select(func.count()).select_from(Ebook).where(Ebook.tenant_id == tenant_id)
    )
    if (count or 0) >= limits["max_ebooks"]:
        raise SubscriptionRequiredError(
            f"Ebook limit reached ({limits['max_ebooks']}). Upgrade your plan to add more ebooks."
        )
