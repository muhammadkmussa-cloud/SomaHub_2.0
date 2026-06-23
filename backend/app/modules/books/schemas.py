import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BookCreate(BaseModel):
    isbn: Optional[str] = Field(None, max_length=32)
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=0, le=3000)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    total_copies: int = Field(1, ge=0)


class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(None, max_length=32)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=0, le=3000)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    cover_url: Optional[str] = None
    total_copies: Optional[int] = Field(None, ge=0)


class BookResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    isbn: Optional[str] = None
    title: str
    author: str
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    total_copies: int
    available_copies: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookCopyCreate(BaseModel):
    book_id: uuid.UUID
    barcode: str = Field(..., min_length=1, max_length=100)
    location: Optional[str] = Field(None, max_length=255)


class BookCopyResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    book_id: uuid.UUID
    barcode: str
    location: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
