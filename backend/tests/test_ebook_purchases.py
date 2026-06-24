"""
Ebook Purchases API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_my_library_empty(async_client, auth_headers):
    """GET /api/v1/ebook-purchases/my-library → empty list."""
    response = await async_client.get(
        "/api/v1/ebook-purchases/my-library", headers=auth_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_ownership(async_client, auth_headers, test_free_ebook):
    """GET /api/v1/ebook-purchases/check/{ebook_id} → owned=false."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.get(
        f"/api/v1/ebook-purchases/check/{ebook_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["owned"] is False


@pytest.mark.asyncio
async def test_checkout_free_ebook(async_client, auth_headers, test_free_ebook):
    """POST /api/v1/ebook-purchases/checkout-free → purchase."""
    ebook_id = str(test_free_ebook.id)

    response = await async_client.post(
        f"/api/v1/ebook-purchases/checkout-free?ebook_id={ebook_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ebook_id"] == ebook_id
    assert float(data["amount"]) == 0.00


@pytest.mark.asyncio
async def test_checkout_free_duplicate(async_client, auth_headers, test_free_ebook):
    """POST /api/v1/ebook-purchases/checkout-free → 400 for duplicate."""
    ebook_id = str(test_free_ebook.id)

    # First checkout
    resp1 = await async_client.post(
        f"/api/v1/ebook-purchases/checkout-free?ebook_id={ebook_id}",
        headers=auth_headers,
    )
    assert resp1.status_code == 200

    # Duplicate
    resp2 = await async_client.post(
        f"/api/v1/ebook-purchases/checkout-free?ebook_id={ebook_id}",
        headers=auth_headers,
    )
    assert resp2.status_code == 400
