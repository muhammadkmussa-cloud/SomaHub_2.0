import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadingProgressCreate(BaseModel):
    ebook_id: uuid.UUID
    progress_percent: int = Field(0, ge=0, le=100)
    last_page: int = Field(1, ge=1)


class ReadingProgressResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ebook_id: uuid.UUID
    progress_percent: int
    last_page: int
    last_opened_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LastReadEbook(BaseModel):
    ebook_id: uuid.UUID
    title: str
    author: str
    cover_url: str | None = None
    progress_percent: int
    last_page: int
    last_opened_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReaderOverviewResponse(BaseModel):
    last_read: LastReadEbook | None = None
    books_completed_this_year: int
    reading_goal_this_year: int
    reading_streak_days: int

    model_config = ConfigDict(from_attributes=True)

