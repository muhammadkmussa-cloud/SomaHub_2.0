import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoanCreate(BaseModel):
    borrower_id: uuid.UUID
    book_copy_id: uuid.UUID
    due_date: date


class LoanResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    borrower_id: uuid.UUID
    book_copy_id: uuid.UUID
    issued_by_user_id: uuid.UUID
    due_date: date
    status: str
    issued_at: datetime
    returned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
