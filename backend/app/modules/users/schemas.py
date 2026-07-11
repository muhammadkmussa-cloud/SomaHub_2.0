import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    display_name: Optional[str] = Field(None, max_length=150)


class UserRoleUpdate(BaseModel):
    role: str = Field(
        ..., description="Role of the user (e.g. reader, librarian, library_admin)"
    )


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    email: EmailStr
    username: str
    role: str
    is_active: bool
    is_email_verified: bool
    avatar_url: Optional[str] = None
    display_name: Optional[str] = None
    timezone: str
    theme: str
    notification_prefs: dict
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


class PreferencesUpdate(BaseModel):
    timezone: Optional[str] = Field(None, max_length=60)
    theme: Optional[str] = Field(None, max_length=20)
    notification_prefs: Optional[dict] = None
