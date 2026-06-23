"""
Subscriptions API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_get_subscription_status(async_client, librarian_headers, admin_headers, test_librarian, test_library_admin):
    """GET /api/v1/subscriptions/status → 200 for library_admin."""
    response = await async_client.get("/api/v1/subscriptions/status", headers=admin_headers)
    # Should create a default trial subscription
    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert "status" in data
    assert "starts_at" in data
    assert "ends_at" in data


@pytest.mark.asyncio
async def test_subscription_status_reader_forbidden(async_client, auth_headers):
    """GET /api/v1/subscriptions/status → 403 for reader."""
    response = await async_client.get("/api/v1/subscriptions/status", headers=auth_headers)
    assert response.status_code == 403
