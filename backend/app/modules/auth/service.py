"""
Auth service — business logic for login, signup, refresh, logout, password reset.
"""

import logging
from datetime import timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.email import send_email, EmailSendError
from app.core.plan_limits import enforce_user_limit
from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    InvalidTokenError,
    NotFoundError,
)
from app.core.redis import (
    delete_refresh_token,
    delete_short_token,
    get_refresh_token,
    get_short_token,
    store_refresh_token,
    store_short_token,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_short_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.auth.models import User
from app.modules.auth.repository import TenantRepository, UserRepository
from app.modules.auth.schemas import (
    LibrarySignupRequest,
    LoginRequest,
    ReaderSignupRequest,
    TokenResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.tenant_repo = TenantRepository(session)

    async def _send_verification_email(self, user: User) -> None:
        token = create_short_token(
            str(user.id),
            "verify",
            expires_minutes=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS * 60,
        )
        ttl = settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS * 60 * 60
        await store_short_token("verify", str(user.id), token, ttl)

        verify_link = f"{settings.FRONTEND_URL}/auth/verify-email?token={token}"
        subject = "Verify your SomaHub email"
        text = (
            f"Hello {user.username},\n\n"
            "Please verify your email address by clicking the link below:\n"
            f"{verify_link}\n\n"
            "If you did not create this account, please ignore this message.\n"
        )
        html = (
            f"<p>Hello {user.username},</p>"
            "<p>Please verify your email address by clicking the link below:</p>"
            f'<p><a href="{verify_link}">Verify Email</a></p>'
            "<p>If you did not create this account, you can safely ignore this email.</p>"
        )
        try:
            await send_email(user.email, subject, html, text)
        except EmailSendError as e:
            logger.warning("Email send failed (console fallback used): %s", e)

    # ── Login ─────────────────────────────────────────────────────────
    async def login(self, payload: LoginRequest) -> tuple[TokenResponse, str]:
        """
        Authenticate user credentials.
        Returns (token_response, refresh_token).
        """
        user = await self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password.")

        if not user.is_active:
            raise AuthenticationError("Your account has been deactivated.")

        # Build tokens
        tenant_id = str(user.tenant_id) if user.tenant_id else None
        access_token = create_access_token(
            subject=str(user.id),
            role=user.role,
            tenant_id=tenant_id,
        )
        refresh_token = create_refresh_token(
            subject=str(user.id),
            role=user.role,
            tenant_id=tenant_id,
        )

        # Persist refresh token in Redis
        ttl = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        await store_refresh_token(str(user.id), refresh_token, ttl)

        # Update last login
        await self.user_repo.update_last_login(user.id)
        await self.session.commit()

        return (
            TokenResponse(
                access_token=access_token,
                role=user.role,
                user_id=str(user.id),
                tenant_id=tenant_id,
            ),
            refresh_token,
        )

    # ── Reader Signup ─────────────────────────────────────────────────
    async def signup_reader(self, payload: ReaderSignupRequest) -> User:
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise AlreadyExistsError("Email")

        user = await self.user_repo.create(
            email=payload.email,
            username=payload.username,
            hashed_password=hash_password(payload.password),
            role="reader",
        )
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user)
        return user

    # ── Library Signup ────────────────────────────────────────────────
    async def signup_library(self, payload: LibrarySignupRequest) -> User:
        # Check email uniqueness for tenant and admin user
        existing_user = await self.user_repo.get_by_email(payload.email)
        if existing_user:
            raise AlreadyExistsError("Email")

        existing_tenant = await self.tenant_repo.get_by_email(payload.email)
        if existing_tenant:
            raise AlreadyExistsError("Library email")

        # Create tenant
        slug = await self.tenant_repo.generate_unique_slug(payload.library_name)
        tenant = await self.tenant_repo.create(
            name=payload.library_name,
            slug=slug,
            email=payload.email,
            library_type=payload.library_type,
            location=payload.location,
        )

        # Create library admin user
        await enforce_user_limit(self.session, tenant.id)
        user = await self.user_repo.create(
            tenant_id=tenant.id,
            email=payload.email,
            username=payload.admin_username,
            hashed_password=hash_password(payload.password),
            role="library_admin",
        )
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user)
        return user

    # ── Refresh Token ─────────────────────────────────────────────────
    async def refresh_tokens(self, refresh_token: str) -> tuple[TokenResponse, str]:
        """
        Validate refresh token and issue new access + refresh token pair.
        """
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise InvalidTokenError("Refresh token is invalid or expired.")

        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type.")

        user_id = payload["sub"]

        # Verify stored token matches
        stored = await get_refresh_token(user_id)
        if stored != refresh_token:
            raise InvalidTokenError("Refresh token has been revoked.")

        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive.")

        tenant_id = str(user.tenant_id) if user.tenant_id else None
        new_access = create_access_token(str(user.id), user.role, tenant_id)
        new_refresh = create_refresh_token(str(user.id), user.role, tenant_id)

        ttl = int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
        await store_refresh_token(user_id, new_refresh, ttl)

        return (
            TokenResponse(
                access_token=new_access,
                role=user.role,
                user_id=str(user.id),
                tenant_id=tenant_id,
            ),
            new_refresh,
        )

    # ── Logout ────────────────────────────────────────────────────────
    async def logout(self, user_id: str) -> None:
        await delete_refresh_token(user_id)

    # ── Forgot Password ───────────────────────────────────────────────
    async def forgot_password(self, email: str) -> None:
        """Always succeeds to avoid email enumeration."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return  # Silent fail

        token = create_short_token(
            str(user.id),
            "reset",
            expires_minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES,
        )
        ttl = settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES * 60
        await store_short_token("reset", str(user.id), token, ttl)

        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={token}"
        subject = "Reset your SomaHub password"
        text = (
            f"Hello {user.username},\n\n"
            "A password reset was requested for your account. Click the link below to reset your password:\n"
            f"{reset_link}\n\n"
            "If you did not request this, you can ignore this message.\n"
        )
        html = (
            f"<p>Hello {user.username},</p>"
            "<p>A password reset was requested for your account. Click the link below to reset your password:</p>"
            f'<p><a href="{reset_link}">Reset Password</a></p>'
            "<p>If you did not request this, you can ignore this email.</p>"
        )
        await send_email(user.email, subject, html, text)

    # ── Reset Password ────────────────────────────────────────────────
    async def reset_password(self, token: str, new_password: str) -> None:
        try:
            payload = decode_token(token)
        except Exception:
            raise InvalidTokenError("Reset token is invalid or expired.")

        if payload.get("purpose") != "reset":
            raise InvalidTokenError("Invalid token purpose.")

        user_id = payload["sub"]
        stored = await get_short_token("reset", user_id)
        if stored != token:
            raise InvalidTokenError("Reset token has already been used.")

        hashed = hash_password(new_password)
        await self.user_repo.update_password(user_id, hashed)  # type: ignore[arg-type]
        await delete_short_token("reset", user_id)
        await self.session.commit()

    # ── Verify Email ──────────────────────────────────────────────────
    async def verify_email(self, token: str) -> None:
        try:
            payload = decode_token(token)
        except Exception:
            raise InvalidTokenError("Verification token is invalid or expired.")

        if payload.get("purpose") != "verify":
            raise InvalidTokenError("Invalid token purpose.")

        user_id = payload["sub"]
        stored = await get_short_token("verify", user_id)
        if stored != token:
            raise InvalidTokenError("Verification token has already been used.")

        await self.user_repo.set_email_verified(user_id)  # type: ignore[arg-type]
        await delete_short_token("verify", user_id)
        await self.session.commit()
