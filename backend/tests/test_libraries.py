"""
Libraries API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_get_library_profile(async_client, librarian_headers, test_librarian):
    """GET /api/v1/libraries/profile → 200."""
    response = await async_client.get(
        "/api/v1/libraries/profile", headers=librarian_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "tenant_id" in data


@pytest.mark.asyncio
async def test_update_library_profile(async_client, admin_headers):
    """PUT /api/v1/libraries/profile → update."""
    response = await async_client.put(
        "/api/v1/libraries/profile",
        json={"name": "Updated Library Name", "description": "A great library."},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Library Name"


@pytest.mark.asyncio
async def test_update_library_profile_reader_forbidden(async_client, auth_headers):
    """PUT /api/v1/libraries/profile → 403 for reader."""
    response = await async_client.put(
        "/api/v1/libraries/profile",
        json={"name": "Hacked Name"},
        headers=auth_headers,
    )
    assert response.status_code == 403
