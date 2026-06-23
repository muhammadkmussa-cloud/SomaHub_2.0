"""
Bookmarks API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_list_bookmarks(async_client, auth_headers, test_free_ebook):
    """GET /api/v1/bookmarks/ebook/{ebook_id} → list."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.get(f"/api/v1/bookmarks/ebook/{ebook_id}", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_bookmark(async_client, auth_headers, test_free_ebook):
    """POST /api/v1/bookmarks → 201 for free ebook."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.post(
        "/api/v1/bookmarks",
        json={"ebook_id": ebook_id, "page": 42, "note": "Important insight!"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["page"] == 42
    assert data["note"] == "Important insight!"


@pytest.mark.asyncio
async def test_delete_bookmark(async_client, auth_headers, test_free_ebook):
    """DELETE /api/v1/bookmarks/{id} → 204."""
    bm = await async_client.post(
        "/api/v1/bookmarks",
        json={"ebook_id": str(test_free_ebook.id), "page": 10},
        headers=auth_headers,
    )
    bm_id = bm.json()["id"]

    response = await async_client.delete(f"/api/v1/bookmarks/{bm_id}", headers=auth_headers)
    assert response.status_code == 204
