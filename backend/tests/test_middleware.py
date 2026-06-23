"""Request logging middleware tests."""

import pytest
from starlette.requests import Request
from starlette.responses import Response

from app.core.middleware import RequestLoggingMiddleware


@pytest.mark.asyncio
async def test_request_logging_adds_request_id_header():
    middleware = RequestLoggingMiddleware(app=None)

    async def call_next(request: Request) -> Response:
        return Response("ok", status_code=200)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/health",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)

    response = await middleware.dispatch(request, call_next)

    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert request.state.request_id
