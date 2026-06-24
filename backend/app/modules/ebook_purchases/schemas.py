import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.ebooks.schemas import EbookResponse


class EbookPurchaseCreate(BaseModel):
    ebook_id: uuid.UUID
    amount: float
    currency: str = "USD"
    payment_id: Optional[uuid.UUID] = None


class EbookPurchaseResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ebook_id: uuid.UUID
    amount: float
    currency: str
    payment_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    ebook: Optional[EbookResponse] = None

    model_config = ConfigDict(from_attributes=True)
