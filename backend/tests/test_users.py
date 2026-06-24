"""
Users API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_get_my_profile(async_client, auth_headers):
    """GET /api/v1/users/me → 200."""
    response = await async_client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["role"] == "reader"


@pytest.mark.asyncio
async def test_update_my_profile(async_client, auth_headers):
    """PATCH /api/v1/users/me → updated fields."""
    response = await async_client.patch(
        "/api/v1/users/me",
        json={"username": "newname"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["username"] == "newname"


@pytest.mark.asyncio
async def test_list_users_reader_forbidden(async_client, auth_headers):
    """GET /api/v1/users → 403 for reader."""
    response = await async_client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_users_librarian(async_client, librarian_headers, test_librarian):
    """GET /api/v1/users → 200 for librarian."""
    response = await async_client.get("/api/v1/users", headers=librarian_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_users_super_admin(
    async_client, super_admin_headers, test_super_admin
):
    """GET /api/v1/users → 200 for super admin."""
    response = await async_client.get("/api/v1/users", headers=super_admin_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_user_role(async_client, admin_headers, test_librarian):
    """PATCH /api/v1/users/{id}/role → updated role."""
    user_id = test_librarian.id
    response = await async_client.patch(
        f"/api/v1/users/{user_id}/role",
        json={"role": "librarian"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "librarian"
