"""
Books & Book Copies API tests.
"""

import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_book(async_client, test_librarian, librarian_headers):
    """POST /api/v1/books → 200 with valid librarian auth."""
    payload = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "category": "Fiction",
        "total_copies": 3,
    }
    response = await async_client.post(
        "/api/v1/books", json=payload, headers=librarian_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Great Gatsby"
    assert data["total_copies"] == 3
    assert data["available_copies"] == 3
    assert "id" in data


@pytest.mark.asyncio
async def test_create_book_unauthorized(async_client, test_user, auth_headers):
    """POST /api/v1/books → 403 for readers."""
    payload = {
        "title": "Test Book",
        "author": "Test Author",
        "total_copies": 1,
    }
    response = await async_client.post(
        "/api/v1/books", json=payload, headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_books(async_client, test_librarian, librarian_headers):
    """GET /api/v1/books → list of books."""
    # Create a book first
    payload = {"title": "1984", "author": "George Orwell", "total_copies": 2}
    await async_client.post("/api/v1/books", json=payload, headers=librarian_headers)

    response = await async_client.get("/api/v1/books", headers=librarian_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(b["title"] == "1984" for b in data)


@pytest.mark.asyncio
async def test_get_book(async_client, test_librarian, librarian_headers):
    """GET /api/v1/books/{id} → single book."""
    payload = {"title": "Brave New World", "author": "Aldous Huxley", "total_copies": 1}
    created = await async_client.post(
        "/api/v1/books", json=payload, headers=librarian_headers
    )
    book_id = created.json()["id"]

    response = await async_client.get(
        f"/api/v1/books/{book_id}", headers=librarian_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Brave New World"


@pytest.mark.asyncio
async def test_get_book_not_found(async_client, librarian_headers):
    """GET /api/v1/books/{id} → 404 for non-existent book."""
    response = await async_client.get(
        f"/api/v1/books/{uuid4()}", headers=librarian_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book(async_client, test_librarian, librarian_headers):
    """PATCH /api/v1/books/{id} → update book."""
    payload = {"title": "Original Title", "author": "Author", "total_copies": 1}
    created = await async_client.post(
        "/api/v1/books", json=payload, headers=librarian_headers
    )
    book_id = created.json()["id"]

    response = await async_client.patch(
        f"/api/v1/books/{book_id}",
        json={"title": "Updated Title"},
        headers=librarian_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_book(
    async_client, test_librarian, test_library_admin, admin_headers, librarian_headers
):
    """DELETE /api/v1/books/{id} → 204 for library admin."""
    payload = {"title": "To Delete", "author": "Author", "total_copies": 1}
    created = await async_client.post(
        "/api/v1/books", json=payload, headers=librarian_headers
    )
    book_id = created.json()["id"]

    response = await async_client.delete(
        f"/api/v1/books/{book_id}", headers=admin_headers
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_book_copy(async_client, test_librarian, librarian_headers):
    """POST /api/v1/book-copies → create new copy."""
    # Create book first
    book_resp = await async_client.post(
        "/api/v1/books",
        json={"title": "Copy Test", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    book_id = book_resp.json()["id"]

    response = await async_client.post(
        "/api/v1/book-copies",
        json={"book_id": book_id, "barcode": "CPY-001", "location": "Shelf A1"},
        headers=librarian_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["barcode"] == "CPY-001"
    assert data["status"] == "available"


@pytest.mark.asyncio
async def test_list_book_copies(async_client, test_librarian, librarian_headers):
    """GET /api/v1/book-copies → list copies."""
    response = await async_client.get("/api/v1/book-copies", headers=librarian_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_search_books(async_client, test_librarian, librarian_headers):
    """GET /api/v1/books?search=... → filtered results."""
    await async_client.post(
        "/api/v1/books",
        json={"title": "UniqueSearchTitle", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )

    response = await async_client.get(
        "/api/v1/books?search=UniqueSearchTitle", headers=librarian_headers
    )
    assert response.status_code == 200
    assert any(b["title"] == "UniqueSearchTitle" for b in response.json())
