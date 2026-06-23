"""
Analytics API tests.
"""

import pytest


@pytest.mark.asyncio
async def test_get_dashboard_super_admin(async_client, test_user, test_librarian, test_library_admin, super_admin_headers):
    """GET /api/v1/analytics/dashboard → 200 for super admin (no tenant scope)."""
    response = await async_client.get("/api/v1/analytics/dashboard", headers=super_admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_books" in data
    assert "total_borrowers" in data
    assert "active_loans" in data
    assert "overdue_loans" in data


@pytest.mark.asyncio
async def test_get_dashboard_librarian(async_client, test_librarian, librarian_headers):
    """GET /api/v1/analytics/dashboard → 200 for librarian."""
    response = await async_client.get("/api/v1/analytics/dashboard", headers=librarian_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_dashboard_reader_forbidden(async_client, auth_headers):
    """GET /api/v1/analytics/dashboard → 403 for reader."""
    response = await async_client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_trends(async_client, librarian_headers, test_librarian):
    """GET /api/v1/analytics/trends → 200."""
    response = await async_client.get("/api/v1/analytics/trends?days=7", headers=librarian_headers)
    assert response.status_code == 200
    data = response.json()
    assert "trends" in data


@pytest.mark.asyncio
async def test_get_top_books(async_client, librarian_headers, test_librarian):
    """GET /api/v1/analytics/books → 200."""
    response = await async_client.get("/api/v1/analytics/books?limit=5", headers=librarian_headers)
    assert response.status_code == 200
    data = response.json()
    assert "books" in data

    # Add a fixture for super_admin since it's not in conftest
