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


@pytest.mark.asyncio
async def test_update_preferences(async_client, auth_headers):
    """PATCH /api/v1/users/me/preferences → 200 and returns updated user preferences."""
    response = await async_client.patch(
        "/api/v1/users/me/preferences",
        json={
            "timezone": "America/New_York",
            "theme": "dark",
            "notification_prefs": {"email_notifs": False, "security_alerts": True}
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["timezone"] == "America/New_York"
    assert data["theme"] == "dark"
    assert data["notification_prefs"]["email_notifs"] is False


@pytest.mark.asyncio
async def test_get_sessions(async_client, auth_headers):
    """GET /api/v1/users/me/sessions → 200 and lists active sessions."""
    response = await async_client.get("/api/v1/users/me/sessions", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_change_password(async_client, auth_headers):
    """POST /api/v1/users/me/change-password → 200 and works."""
    response = await async_client.post(
        "/api/v1/users/me/change-password",
        json={
            "current_password": "password123",
            "new_password": "newpassword123"
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "message" in response.json()
