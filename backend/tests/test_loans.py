"""
Loans API tests.
"""

import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_issue_loan(async_client, librarian_headers, test_librarian):
    """POST /api/v1/loans → 200."""
    # Create a borrower
    borrower_resp = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Loan", "last_name": "Test", "student_id": "LOAN-001"},
        headers=librarian_headers,
    )
    borrower_id = borrower_resp.json()["id"]

    # Create a book and copy
    book_resp = await async_client.post(
        "/api/v1/books",
        json={"title": "Loanable", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    book_id = book_resp.json()["id"]

    copy_resp = await async_client.post(
        "/api/v1/book-copies",
        json={"book_id": book_id, "barcode": "LOAN-CPY-001"},
        headers=librarian_headers,
    )
    copy_id = copy_resp.json()["id"]

    due = (date.today() + timedelta(days=14)).isoformat()
    response = await async_client.post(
        "/api/v1/loans",
        json={"borrower_id": borrower_id, "book_copy_id": copy_id, "due_date": due},
        headers=librarian_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "issued"
    assert data["borrower_id"] == borrower_id


@pytest.mark.asyncio
async def test_issue_loan_suspended_borrower(
    async_client, librarian_headers, admin_headers
):
    """POST /api/v1/loans → 409 for suspended borrower."""
    # Create borrower
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Suspended", "last_name": "Borrower"},
        headers=librarian_headers,
    )
    borrower_id = br.json()["id"]

    # Suspend
    await async_client.post(
        f"/api/v1/borrowers/{borrower_id}/suspend", headers=admin_headers
    )

    # Create book + copy
    bk = await async_client.post(
        "/api/v1/books",
        json={"title": "SuspendedTest", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    cp = await async_client.post(
        "/api/v1/book-copies",
        json={"book_id": bk.json()["id"], "barcode": "SUS-CPY"},
        headers=librarian_headers,
    )

    due = (date.today() + timedelta(days=14)).isoformat()
    response = await async_client.post(
        "/api/v1/loans",
        json={
            "borrower_id": borrower_id,
            "book_copy_id": cp.json()["id"],
            "due_date": due,
        },
        headers=librarian_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_loans(async_client, librarian_headers):
    """GET /api/v1/loans → list."""
    response = await async_client.get("/api/v1/loans", headers=librarian_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_return_loan(async_client, librarian_headers):
    """POST /api/v1/loans/{id}/return → returned status."""
    # Create borrower
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Return", "last_name": "Test"},
        headers=librarian_headers,
    )
    # Create book + copy
    bk = await async_client.post(
        "/api/v1/books",
        json={"title": "Returnable", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    cp = await async_client.post(
        "/api/v1/book-copies",
        json={"book_id": bk.json()["id"], "barcode": "RET-CPY"},
        headers=librarian_headers,
    )
    # Issue loan
    due = (date.today() + timedelta(days=14)).isoformat()
    loan = await async_client.post(
        "/api/v1/loans",
        json={
            "borrower_id": br.json()["id"],
            "book_copy_id": cp.json()["id"],
            "due_date": due,
        },
        headers=librarian_headers,
    )
    loan_id = loan.json()["id"]

    # Return
    response = await async_client.post(
        f"/api/v1/loans/{loan_id}/return", headers=librarian_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "returned"


@pytest.mark.asyncio
async def test_mark_lost(async_client, librarian_headers):
    """POST /api/v1/loans/{id}/lost → lost status + fine created."""
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "Lost", "last_name": "Test"},
        headers=librarian_headers,
    )
    bk = await async_client.post(
        "/api/v1/books",
        json={"title": "Losable", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    cp = await async_client.post(
        "/api/v1/book-copies",
        json={"book_id": bk.json()["id"], "barcode": "LOST-CPY"},
        headers=librarian_headers,
    )
    due = (date.today() + timedelta(days=14)).isoformat()
    loan = await async_client.post(
        "/api/v1/loans",
        json={
            "borrower_id": br.json()["id"],
            "book_copy_id": cp.json()["id"],
            "due_date": due,
        },
        headers=librarian_headers,
    )
    loan_id = loan.json()["id"]

    response = await async_client.post(
        f"/api/v1/loans/{loan_id}/lost", headers=librarian_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "lost"


@pytest.mark.asyncio
async def test_issue_loan_unavailable_copy(async_client, librarian_headers):
    """POST /api/v1/loans → 409 for already-loaned copy."""
    br = await async_client.post(
        "/api/v1/borrowers",
        json={"first_name": "First", "last_name": "Borrower"},
        headers=librarian_headers,
    )
    bk = await async_client.post(
        "/api/v1/books",
        json={"title": "SingleCopy", "author": "Author", "total_copies": 1},
        headers=librarian_headers,
    )
    cp = await async_client.post(
        "/api/v1/book-copies",
        json={"book_id": bk.json()["id"], "barcode": "SINGLE-CPY"},
        headers=librarian_headers,
    )

    due = (date.today() + timedelta(days=14)).isoformat()
    # Issue first loan — should succeed
    resp1 = await async_client.post(
        "/api/v1/loans",
        json={
            "borrower_id": br.json()["id"],
            "book_copy_id": cp.json()["id"],
            "due_date": due,
        },
        headers=librarian_headers,
    )
    assert resp1.status_code == 200

    # Try issuing the same copy again — should fail
    resp2 = await async_client.post(
        "/api/v1/loans",
        json={
            "borrower_id": br.json()["id"],
            "book_copy_id": cp.json()["id"],
            "due_date": due,
        },
        headers=librarian_headers,
    )
    assert resp2.status_code == 409
