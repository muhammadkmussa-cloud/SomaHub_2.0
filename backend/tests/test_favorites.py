"""
Favorites API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_list_favorites(async_client, auth_headers):
    """GET /api/v1/favorites → list (empty initially)."""
    response = await async_client.get("/api/v1/favorites", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_favorite(async_client, auth_headers, test_free_ebook):
    """POST /api/v1/favorites → 201."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.post(
        "/api/v1/favorites",
        json={"ebook_id": ebook_id},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ebook_id"] == ebook_id


@pytest.mark.asyncio
async def test_remove_favorite(async_client, auth_headers, test_free_ebook):
    """DELETE /api/v1/favorites/{ebook_id} → 204."""
    ebook_id = str(test_free_ebook.id)

    # Add first
    await async_client.post(
        "/api/v1/favorites",
        json={"ebook_id": ebook_id},
        headers=auth_headers,
    )

    # Remove
    response = await async_client.delete(f"/api/v1/favorites/{ebook_id}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_add_duplicate_favorite(async_client, auth_headers, test_free_ebook):
    """POST /api/v1/favorites → idempotent (returns existing)."""
    ebook_id = str(test_free_ebook.id)

    resp1 = await async_client.post(
        "/api/v1/favorites",
        json={"ebook_id": ebook_id},
        headers=auth_headers,
    )
    assert resp1.status_code == 201

    resp2 = await async_client.post(
        "/api/v1/favorites",
        json={"ebook_id": ebook_id},
        headers=auth_headers,
    )
    # Should return the existing favorite (idempotent)
    assert resp2.status_code in (200, 201)
