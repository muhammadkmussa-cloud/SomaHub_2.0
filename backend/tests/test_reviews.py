"""
Reviews API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_list_reviews(async_client, auth_headers, test_free_ebook):
    """GET /api/v1/reviews/ebook/{ebook_id} → list."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.get(
        f"/api/v1/reviews/ebook/{ebook_id}", headers=auth_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_review_free_ebook(
    async_client, auth_headers, test_user, test_free_ebook
):
    """POST /api/v1/reviews → 201 for free ebook (no purchase required)."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.post(
        "/api/v1/reviews",
        json={"ebook_id": ebook_id, "rating": 5, "comment": "Great book!"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["comment"] == "Great book!"


@pytest.mark.asyncio
async def test_update_review(async_client, auth_headers, test_free_ebook):
    """PUT /api/v1/reviews/{id} → update."""
    ebook_id = str(test_free_ebook.id)

    review = await async_client.post(
        "/api/v1/reviews",
        json={"ebook_id": ebook_id, "rating": 3},
        headers=auth_headers,
    )
    review_id = review.json()["id"]

    response = await async_client.put(
        f"/api/v1/reviews/{review_id}",
        json={"rating": 4, "comment": "Updated"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 4


@pytest.mark.asyncio
async def test_delete_review(async_client, auth_headers, test_free_ebook):
    """DELETE /api/v1/reviews/{id} → 204."""
    ebook_id = str(test_free_ebook.id)

    review = await async_client.post(
        "/api/v1/reviews",
        json={"ebook_id": ebook_id, "rating": 2},
        headers=auth_headers,
    )
    review_id = review.json()["id"]

    response = await async_client.delete(
        f"/api/v1/reviews/{review_id}", headers=auth_headers
    )
    assert response.status_code == 204
