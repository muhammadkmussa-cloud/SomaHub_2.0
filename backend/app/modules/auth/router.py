"""
Auth API router — all authentication endpoints.
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.rate_limit import enforce_rate_limit
from app.core.redis import blacklist_token
from app.core.security import decode_token
from app.modules.auth.schemas import (
    ForgotPasswordRequest,
    LibrarySignupRequest,
    LoginRequest,
    ReaderSignupRequest,
    ResetPasswordRequest,
    SuccessResponse,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Cookie config
REFRESH_COOKIE_KEY = "somahub_refresh"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


def _cookie_secure() -> bool:
    return settings.cookie_secure


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_KEY)


# ── Login ─────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
):
    """Authenticate a user and return JWT access token."""
    await enforce_rate_limit(request, "auth:login")
    service = AuthService(session)
    token_response, refresh_token = await service.login(payload)
    _set_refresh_cookie(response, refresh_token)
    return token_response


# ── Reader Signup ─────────────────────────────────────────────────────────────
@router.post("/signup/reader", response_model=SuccessResponse, status_code=201)
async def signup_reader(
    payload: ReaderSignupRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Register a new reader account."""
    await enforce_rate_limit(request, "auth:signup")
    service = AuthService(session)
    user = await service.signup_reader(payload)
    return SuccessResponse(
        message="Account created successfully. Please verify your email.",
        data={"user_id": str(user.id)},
    )


# ── Library Signup ────────────────────────────────────────────────────────────
@router.post("/signup/library", response_model=SuccessResponse, status_code=201)
async def signup_library(
    payload: LibrarySignupRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Register a new library institution with an admin account."""
    await enforce_rate_limit(request, "auth:signup")
    service = AuthService(session)
    user = await service.signup_library(payload)
    return SuccessResponse(
        message="Library account created successfully. Please verify your email.",
        data={"user_id": str(user.id)},
    )


# ── Refresh Token ─────────────────────────────────────────────────────────────
@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    response: Response,
    refresh_token: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    """
    Issue a new access token using the refresh token from the HTTP-only cookie.
    """

    service = AuthService(session)
    token_response, new_refresh = await service.refresh_tokens(refresh_token or "")
    _set_refresh_cookie(response, new_refresh)
    return token_response


@router.post("/refresh-cookie")
async def refresh_from_cookie(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db),
):
    """Refresh using the HTTP-only cookie (preferred). Returns 401 if no valid cookie."""
    from fastapi import HTTPException as _HTTPException

    token = request.cookies.get(REFRESH_COOKIE_KEY, "")
    if not token:
        raise _HTTPException(status_code=401, detail="No refresh token cookie found.")

    service = AuthService(session)
    try:
        token_response, new_refresh = await service.refresh_tokens(token)
        _set_refresh_cookie(response, new_refresh)
        return token_response
    except Exception:
        _clear_refresh_cookie(response)
        raise _HTTPException(status_code=401, detail="Session expired. Please log in again.")


# ── Logout ────────────────────────────────────────────────────────────────────
@router.post("/logout", response_model=SuccessResponse)
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    """Logout the current user and revoke their refresh token."""
    service = AuthService(session)
    await service.logout(current_user.user_id)

    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            if jti:
                ttl = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                await blacklist_token(jti, ttl)
        except Exception:
            pass

    _clear_refresh_cookie(response)
    return SuccessResponse(message="Logged out successfully.")


# ── Forgot Password ───────────────────────────────────────────────────────────
@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Send a password reset email if the email is registered."""
    await enforce_rate_limit(request, "auth:forgot-password")
    service = AuthService(session)
    await service.forgot_password(payload.email)
    return SuccessResponse(
        message="If that email is registered, a reset link has been sent."
    )


# ── Reset Password ────────────────────────────────────────────────────────────
@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    session: AsyncSession = Depends(get_db),
):
    """Reset user password using a valid reset token."""
    service = AuthService(session)
    await service.reset_password(payload.token, payload.new_password)
    return SuccessResponse(message="Password reset successfully. You can now log in.")


# ── Verify Email ──────────────────────────────────────────────────────────────
@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    session: AsyncSession = Depends(get_db),
):
    """Verify user email address using a verification token."""
    service = AuthService(session)
    await service.verify_email(payload.token)
    return SuccessResponse(message="Email verified successfully.")


# ── Me ────────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    """Return the currently authenticated user's profile."""
    from app.modules.auth.repository import UserRepository
    from uuid import UUID

    repo = UserRepository(session)
    user = await repo.get_by_id(UUID(current_user.user_id))
    if not user:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("User")
    return UserResponse.model_validate(user)
