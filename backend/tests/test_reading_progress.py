"""
Reading Progress API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_get_progress(async_client, auth_headers, test_free_ebook):
    """GET /api/v1/reading-progress/{ebook_id} → 200."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.get(
        f"/api/v1/reading-progress/{ebook_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["progress_percent"] == 0
    assert data["last_page"] == 1


@pytest.mark.asyncio
async def test_update_progress(async_client, auth_headers, test_free_ebook):
    """POST /api/v1/reading-progress → update progress."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.post(
        "/api/v1/reading-progress",
        json={"ebook_id": ebook_id, "progress_percent": 50, "last_page": 100},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["progress_percent"] == 50
    assert data["last_page"] == 100
