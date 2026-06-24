"""
Borrowers API tests.
"""

import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_borrower(async_client, librarian_headers):
    """POST /api/v1/borrowers → 200."""
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "+254700000000",
        "student_id": "STU-001",
    }
    response = await async_client.post(
        "/api/v1/borrowers", json=payload, headers=librarian_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john@example.com"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_create_borrower_unauthorized(async_client, auth_headers):
    """POST /api/v1/borrowers → 403 for readers."""
    payload = {"first_name": "Test", "last_name": "User"}
    response = await async_client.post(
        "/api/v1/borrowers", json=payload, headers=auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_borrowers(async_client, librarian_headers):
    """GET /api/v1/borrowers → list."""
    # Create a borrower
    await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Jane", "last_name": "Smith", "student_id": "STU-002"},
        headers=librarian_headers,
    )

    response = await async_client.get("/api/v1/borrowers", headers=librarian_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(b["first_name"] == "Jane" for b in data)


@pytest.mark.asyncio
async def test_get_borrower(async_client, librarian_headers):
    """GET /api/v1/borrowers/{id} → single borrower."""
    created = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Alice", "last_name": "Wonderland"},
        headers=librarian_headers,
    )
    borrower_id = created.json()["id"]

    response = await async_client.get(
        f"/api/v1/borrowers/{borrower_id}", headers=librarian_headers
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Alice"


@pytest.mark.asyncio
async def test_get_borrower_not_found(async_client, librarian_headers):
    """GET /api/v1/borrowers/{id} → 404."""
    response = await async_client.get(
        f"/api/v1/borrowers/{uuid4()}", headers=librarian_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_suspend_borrower(
    async_client, librarian_headers, admin_headers, test_library_admin
):
    """POST /api/v1/borrowers/{id}/suspend → suspended status."""
    created = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Bad", "last_name": "Actor"},
        headers=librarian_headers,
    )
    borrower_id = created.json()["id"]

    response = await async_client.post(
        f"/api/v1/borrowers/{borrower_id}/suspend",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "suspended"


@pytest.mark.asyncio
async def test_update_borrower(async_client, librarian_headers):
    """PATCH /api/v1/borrowers/{id} → updated fields."""
    created = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Old", "last_name": "Name"},
        headers=librarian_headers,
    )
    borrower_id = created.json()["id"]

    response = await async_client.patch(
        f"/api/v1/borrowers/{borrower_id}",
        json={"first_name": "New"},
        headers=librarian_headers,
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "New"
