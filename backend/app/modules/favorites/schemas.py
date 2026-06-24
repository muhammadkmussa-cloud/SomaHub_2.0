import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.ebooks.schemas import EbookResponse


class FavoriteCreate(BaseModel):
    ebook_id: uuid.UUID


class FavoriteResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ebook_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    ebook: EbookResponse

    model_config = ConfigDict(from_attributes=True)
