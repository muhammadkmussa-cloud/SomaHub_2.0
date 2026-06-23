import json
import logging
import sys
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.tenant import get_current_tenant_id

logger = logging.getLogger("somahub.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()

        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        tenant_id = get_current_tenant_id()
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "tenant_id": str(tenant_id) if tenant_id else None,
        }

        if settings.APP_ENV == "development":
            logger.info(
                "%s %s -> %s (%.1fms) [%s]",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
                request_id,
            )
        else:
            logger.info(json.dumps(log_data))

        response.headers["X-Request-ID"] = request_id
        return response
