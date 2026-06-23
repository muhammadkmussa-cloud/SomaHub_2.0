import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BookmarkCreate(BaseModel):
    ebook_id: uuid.UUID
    page: int = Field(..., ge=1)
    note: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ebook_id: uuid.UUID
    page: int
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
