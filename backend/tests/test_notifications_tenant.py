"""Notification tenant filtering tests."""

import pytest
from uuid import uuid4

from app.modules.notifications.models import Notification


@pytest.mark.asyncio
async def test_list_notifications_filters_by_tenant(async_client, test_user, auth_headers, db_session, test_tenant):
    """GET /api/v1/notifications returns only notifications for the user's tenant."""
    other_tenant_id = uuid4()

    db_session.add(
        Notification(
            id=uuid4(),
            user_id=test_user.id,
            tenant_id=test_tenant.id,
            title="In tenant",
            message="Visible",
            category="system",
            status="unread",
        )
    )
    db_session.add(
        Notification(
            id=uuid4(),
            user_id=test_user.id,
            tenant_id=other_tenant_id,
            title="Other tenant",
            message="Hidden",
            category="system",
            status="unread",
        )
    )
    await db_session.commit()

    response = await async_client.get("/api/v1/notifications", headers=auth_headers)
    assert response.status_code == 200
    titles = [n["title"] for n in response.json()]
    assert "In tenant" in titles
    assert "Other tenant" not in titles
