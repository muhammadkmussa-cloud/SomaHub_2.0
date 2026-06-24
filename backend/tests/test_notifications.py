"""
Notifications API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_list_notifications(async_client, auth_headers):
    """GET /api/v1/notifications → list of notifications."""
    response = await async_client.get("/api/v1/notifications", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_mark_notification_read(async_client, auth_headers, test_user):
    """POST /api/v1/notifications/{id}/read → 200."""
    # Get list first
    list_resp = await async_client.get("/api/v1/notifications", headers=auth_headers)
    assert list_resp.status_code == 200
    notifs = list_resp.json()
    if notifs:
        nid = notifs[0]["id"]
        resp = await async_client.post(
            f"/api/v1/notifications/{nid}/read", headers=auth_headers
        )
        assert resp.status_code == 200
