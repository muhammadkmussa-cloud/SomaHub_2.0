import pytest
from datetime import datetime, timezone, timedelta
from app.modules.reading_progress.models import ReadingProgress

@pytest.mark.asyncio
async def test_reader_overview_empty(async_client, auth_headers):
    """GET /api/v1/reader/overview when no books are read."""
    response = await async_client.get("/api/v1/reader/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["last_read"] is None
    assert data["books_completed_this_year"] == 0
    assert data["reading_goal_this_year"] == 12
    assert data["reading_streak_days"] == 0

@pytest.mark.asyncio
async def test_reader_overview_with_progress(async_client, auth_headers, test_free_ebook, db_session, test_user):
    """GET /api/v1/reader/overview with progress in db."""
    # Insert reading progress
    progress = ReadingProgress(
        user_id=test_user.id,
        ebook_id=test_free_ebook.id,
        progress_percent=100,
        last_page=10,
        last_opened_at=datetime.now(timezone.utc),
    )
    db_session.add(progress)
    await db_session.commit()

    response = await async_client.get("/api/v1/reader/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["last_read"] is not None
    assert data["last_read"]["title"] == test_free_ebook.title
    assert data["last_read"]["progress_percent"] == 100
    assert data["books_completed_this_year"] == 1
    assert data["reading_streak_days"] == 1
