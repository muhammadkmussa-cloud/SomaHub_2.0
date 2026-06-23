"""
Authentication API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_login_success(async_client, test_tenant, test_user):
    """POST /api/v1/auth/login with valid credentials → 200 + access_token."""
    payload = {"email": "reader@test.com", "password": "password123"}
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client, test_tenant, test_user):
    """POST /api/v1/auth/login with wrong password → 401."""
    payload = {"email": "reader@test.com", "password": "wrongpassword"}
    response = await async_client.post("/api/v1/auth/login", json=payload)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_signup_reader(async_client, test_tenant):
    """POST /api/v1/auth/signup/reader → 201."""
    payload = {
        "email": "newreader@test.com",
        "username": "newreader",
        "password": "ReaderPass123!",
        "confirm_password": "ReaderPass123!",
    }
    response = await async_client.post("/api/v1/auth/signup/reader", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "user_id" in data["data"]


@pytest.mark.asyncio
async def test_refresh_token(async_client, test_tenant, test_user):
    """POST /api/v1/auth/refresh-cookie → 200 with refresh cookie."""
    login_payload = {"email": "reader@test.com", "password": "password123"}
    login_resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200

    refresh_resp = await async_client.post("/api/v1/auth/refresh-cookie")
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert data.get("access_token")


@pytest.mark.asyncio
async def test_logout(async_client, test_tenant, test_user, auth_headers):
    """POST /api/v1/auth/logout → 200."""
    response = await async_client.post("/api/v1/auth/logout", headers=auth_headers)
    assert response.status_code == 200
