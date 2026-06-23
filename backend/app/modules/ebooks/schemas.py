import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EbookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    price: float = Field(0.00, ge=0.0)
    cover_url: Optional[str] = None
    file_url: Optional[str] = None
    status: str = Field("draft", pattern="^(draft|published|archived)$")


class EbookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, ge=0.0)
    cover_url: Optional[str] = None
    file_url: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published|archived)$")


class EbookResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    cover_url: Optional[str] = None
    file_url: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
