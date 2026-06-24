import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None


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
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
