"""
Custom exception classes and FastAPI exception handlers.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# ── Base ──────────────────────────────────────────────────────────────────────
class SomaHubException(Exception):
    """Base exception for all SomaHub errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ── Auth exceptions ───────────────────────────────────────────────────────────
class AuthenticationError(SomaHubException):
    def __init__(self, message: str = "Authentication failed."):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class TokenExpiredError(SomaHubException):
    def __init__(self, message: str = "Token has expired."):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class InvalidTokenError(SomaHubException):
    def __init__(self, message: str = "Token is invalid."):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(SomaHubException):
    def __init__(
        self, message: str = "You do not have permission to perform this action."
    ):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)


class RateLimitExceededError(SomaHubException):
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(message, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class SubscriptionRequiredError(SomaHubException):
    def __init__(
        self, message: str = "An active subscription is required for this action."
    ):
        super().__init__(message, status_code=status.HTTP_402_PAYMENT_REQUIRED)


# ── Resource exceptions ───────────────────────────────────────────────────────
class NotFoundError(SomaHubException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            f"{resource} not found.", status_code=status.HTTP_404_NOT_FOUND
        )


class AlreadyExistsError(SomaHubException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            f"{resource} already exists.", status_code=status.HTTP_409_CONFLICT
        )


class ValidationError(SomaHubException):
    def __init__(self, message: str = "Validation failed."):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# ── Tenant exceptions ─────────────────────────────────────────────────────────
class TenantNotFoundError(SomaHubException):
    def __init__(self):
        super().__init__("Tenant not found.", status_code=status.HTTP_404_NOT_FOUND)


class TenantSuspendedError(SomaHubException):
    def __init__(self):
        super().__init__(
            "This library account has been suspended.",
            status_code=status.HTTP_403_FORBIDDEN,
        )


# ── Business rule exceptions ──────────────────────────────────────────────────
class InsufficientCopiesError(SomaHubException):
    def __init__(self):
        super().__init__(
            "No copies available to issue.", status_code=status.HTTP_409_CONFLICT
        )


class BorrowerSuspendedError(SomaHubException):
    def __init__(self):
        super().__init__(
            "Borrower account is suspended.", status_code=status.HTTP_403_FORBIDDEN
        )


# ── Handler registration ──────────────────────────────────────────────────────
def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers with the FastAPI app."""

    @app.exception_handler(SomaHubException)
    async def somahub_exception_handler(
        request: Request, exc: SomaHubException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "errors": [],
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "The requested resource was not found.",
                "errors": [],
            },
        )

    @app.exception_handler(405)
    async def method_not_allowed_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=405,
            content={
                "success": False,
                "message": "Method not allowed.",
                "errors": [],
            },
        )
