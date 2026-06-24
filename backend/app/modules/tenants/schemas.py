import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TenantBase(BaseModel):
    name: str = Field(
        ..., max_length=255, description="Name of the library institution"
    )
    slug: str = Field(
        ..., max_length=100, description="Unique URL friendly subdomain/slug"
    )
    email: EmailStr = Field(..., description="Institutional contact email")
    library_type: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    slug: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    library_type: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    plan: Optional[str] = Field(None, max_length=50)


class TenantResponse(TenantBase):
    id: uuid.UUID
    is_active: bool
    plan: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
