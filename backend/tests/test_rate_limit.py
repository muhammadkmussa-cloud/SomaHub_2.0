"""Rate limiting tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_login_rate_limit():
    """Excessive login attempts return 429."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for _ in range(12):
            response = await client.post(
                "/api/v1/auth/login",
                json={"email": "nobody@test.com", "password": "wrong"},
            )
        assert response.status_code == 429
