"""
Ebooks API tests.
"""

import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_ebook(async_client, super_admin_headers):
    """POST /api/v1/ebooks → 201 with super admin auth."""
    payload = {
        "title": "Digital Book",
        "author": "Digital Author",
        "description": "An ebook for testing.",
        "category": "Technology",
        "price": 9.99,
    }
    response = await async_client.post(
        "/api/v1/ebooks", json=payload, headers=super_admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Digital Book"
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_create_ebook_librarian_unauthorized(async_client, librarian_headers):
    """POST /api/v1/ebooks → 403 for librarian."""
    payload = {"title": "Test", "author": "Author", "price": 0.00}
    response = await async_client.post(
        "/api/v1/ebooks", json=payload, headers=librarian_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_ebook_reader_unauthorized(async_client, auth_headers):
    """POST /api/v1/ebooks → 403 for reader."""
    payload = {"title": "Test", "author": "Author", "price": 0.00}
    response = await async_client.post(
        "/api/v1/ebooks", json=payload, headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_ebooks(async_client, auth_headers):
    """GET /api/v1/ebooks → list (readers see only published)."""
    response = await async_client.get("/api/v1/ebooks", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_ebook(async_client, super_admin_headers):
    """GET /api/v1/ebooks/{id} → single ebook."""
    created = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Specific Ebook", "author": "Author", "price": 5.99},
        headers=super_admin_headers,
    )
    ebook_id = created.json()["id"]

    response = await async_client.get(
        f"/api/v1/ebooks/{ebook_id}", headers=super_admin_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Ebook"


@pytest.mark.asyncio
async def test_get_ebook_not_found(async_client, super_admin_headers):
    """GET /api/v1/ebooks/{id} → 404."""
    response = await async_client.get(
        f"/api/v1/ebooks/{uuid4()}", headers=super_admin_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_ebook(async_client, super_admin_headers):
    """PUT /api/v1/ebooks/{id} → updated fields."""
    created = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Original Ebook", "author": "Author", "price": 4.99},
        headers=super_admin_headers,
    )
    ebook_id = created.json()["id"]

    response = await async_client.put(
        f"/api/v1/ebooks/{ebook_id}",
        json={"title": "Updated Ebook", "price": 14.99},
        headers=super_admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Ebook"
    assert float(response.json()["price"]) == 14.99


@pytest.mark.asyncio
async def test_update_ebook_librarian_unauthorized(async_client, super_admin_headers, librarian_headers):
    """PUT /api/v1/ebooks/{id} → 403 for librarian."""
    created = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Original Ebook", "author": "Author", "price": 4.99},
        headers=super_admin_headers,
    )
    ebook_id = created.json()["id"]

    response = await async_client.put(
        f"/api/v1/ebooks/{ebook_id}",
        json={"title": "Updated Ebook", "price": 14.99},
        headers=librarian_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_ebook(async_client, super_admin_headers):
    """DELETE /api/v1/ebooks/{id} → 204."""
    created = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Delete Me", "author": "Author", "price": 0.00},
        headers=super_admin_headers,
    )
    ebook_id = created.json()["id"]

    response = await async_client.delete(
        f"/api/v1/ebooks/{ebook_id}", headers=super_admin_headers
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_ebook_librarian_unauthorized(async_client, super_admin_headers, librarian_headers):
    """DELETE /api/v1/ebooks/{id} → 403 for librarian."""
    created = await async_client.post(
        "/api/v1/ebooks",
        json={"title": "Delete Me", "author": "Author", "price": 0.00},
        headers=super_admin_headers,
    )
    ebook_id = created.json()["id"]

    response = await async_client.delete(
        f"/api/v1/ebooks/{ebook_id}", headers=librarian_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_search_ebooks(async_client, super_admin_headers, auth_headers):
    """GET /api/v1/ebooks?search=... → filtered."""
    await async_client.post(
        "/api/v1/ebooks",
        json={
            "title": "UniqueEbookSearch",
            "author": "Author",
            "price": 0.00,
            "status": "published",
        },
        headers=super_admin_headers,
    )

    response = await async_client.get(
        "/api/v1/ebooks?search=UniqueEbookSearch", headers=auth_headers
    )
    assert response.status_code == 200
    assert any(e["title"] == "UniqueEbookSearch" for e in response.json())


@pytest.mark.asyncio
async def test_bookstore_role_access(async_client, auth_headers, super_admin_headers, librarian_headers):
    """Verify bookstore accessibility for reader, super admin, and librarian."""
    # Reader has access
    response = await async_client.get("/api/v1/bookstore/ebooks", headers=auth_headers)
    assert response.status_code == 200

    # Super Admin has access
    response = await async_client.get("/api/v1/bookstore/ebooks", headers=super_admin_headers)
    assert response.status_code == 200

    # Librarian is denied access
    response = await async_client.get("/api/v1/bookstore/ebooks", headers=librarian_headers)
    assert response.status_code == 403
