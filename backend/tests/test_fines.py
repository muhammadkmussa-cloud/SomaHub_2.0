"""
Fines API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_create_fine(async_client, librarian_headers):
    """POST /api/v1/fines → 200."""
    # Need a borrower first
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Fine", "last_name": "Test"},
        headers=librarian_headers,
    )
    borrower_id = br.json()["id"]

    response = await async_client.post(
        "/api/v1/fines",
        json={"borrower_id": borrower_id, "reason": "damaged_book", "amount": 50.00},
        headers=librarian_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["reason"] == "damaged_book"
    assert data["status"] == "unpaid"
    assert float(data["amount"]) == 50.00


@pytest.mark.asyncio
async def test_list_fines(async_client, librarian_headers):
    """GET /api/v1/fines → list fines."""
    response = await async_client.get("/api/v1/fines", headers=librarian_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_fine(async_client, librarian_headers):
    """GET /api/v1/fines/{id} → single fine."""
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "FineGet", "last_name": "Test"},
        headers=librarian_headers,
    )
    fine = await async_client.post(
        "/api/v1/fines",
        json={"borrower_id": br.json()["id"], "reason": "overdue", "amount": 30.00},
        headers=librarian_headers,
    )
    fine_id = fine.json()["id"]

    response = await async_client.get(
        f"/api/v1/fines/{fine_id}", headers=librarian_headers
    )
    assert response.status_code == 200
    assert response.json()["reason"] == "overdue"


@pytest.mark.asyncio
async def test_pay_fine(async_client, librarian_headers):
    """POST /api/v1/fines/{id}/pay → partial payment."""
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Pay", "last_name": "Fine"},
        headers=librarian_headers,
    )
    fine = await async_client.post(
        "/api/v1/fines",
        json={"borrower_id": br.json()["id"], "reason": "overdue", "amount": 100.00},
        headers=librarian_headers,
    )
    fine_id = fine.json()["id"]

    response = await async_client.post(
        f"/api/v1/fines/{fine_id}/pay",
        json={"amount": 40.00},
        headers=librarian_headers,
    )
    assert response.status_code == 200
    assert float(response.json()["paid_amount"]) == 40.00


@pytest.mark.asyncio
async def test_waive_fine(async_client, librarian_headers, admin_headers):
    """POST /api/v1/fines/{id}/waive → waived status."""
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Waive", "last_name": "Fine"},
        headers=librarian_headers,
    )
    fine = await async_client.post(
        "/api/v1/fines",
        json={"borrower_id": br.json()["id"], "reason": "overdue", "amount": 25.00},
        headers=librarian_headers,
    )
    fine_id = fine.json()["id"]

    response = await async_client.post(
        f"/api/v1/fines/{fine_id}/waive",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "waived"


@pytest.mark.asyncio
async def test_pay_already_paid_fine(async_client, librarian_headers):
    """POST /api/v1/fines/{id}/pay → 409 for paid fine."""
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "DoublePay", "last_name": "Test"},
        headers=librarian_headers,
    )
    fine = await async_client.post(
        "/api/v1/fines",
        json={"borrower_id": br.json()["id"], "reason": "overdue", "amount": 50.00},
        headers=librarian_headers,
    )
    fine_id = fine.json()["id"]

    # Pay in full
    await async_client.post(
        f"/api/v1/fines/{fine_id}/pay",
        json={"amount": 50.00},
        headers=librarian_headers,
    )

    # Try paying again
    response = await async_client.post(
        f"/api/v1/fines/{fine_id}/pay",
        json={"amount": 10.00},
        headers=librarian_headers,
    )
    assert response.status_code == 409
