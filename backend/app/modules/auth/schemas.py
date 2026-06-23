"""
Pydantic schemas for auth request/response validation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Login ─────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    tenant_id: Optional[str] = None


# ── Reader Signup ─────────────────────────────────────────────────────────────
class ReaderSignupRequest(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match.")
        return v


# ── Library Signup ────────────────────────────────────────────────────────────
class LibrarySignupRequest(BaseModel):
    library_name: str = Field(min_length=2, max_length=255)
    admin_username: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    library_type: Optional[str] = None
    location: Optional[str] = None

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match.")
        return v


# ── Password reset ────────────────────────────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match.")
        return v


# ── Email verification ────────────────────────────────────────────────────────
class VerifyEmailRequest(BaseModel):
    token: str


# ── User response ─────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    role: str
    tenant_id: Optional[UUID] = None
    is_active: bool
    is_email_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Standard success wrapper ──────────────────────────────────────────────────
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None
