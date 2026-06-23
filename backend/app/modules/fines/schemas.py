import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FineCreate(BaseModel):
    borrower_id: uuid.UUID
    loan_id: Optional[uuid.UUID] = None
    reason: str = Field(..., min_length=1, max_length=100)
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    notes: Optional[str] = None


class FinePayment(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)


class FineResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    borrower_id: uuid.UUID
    loan_id: Optional[uuid.UUID] = None
    reason: str
    amount: Decimal
    paid_amount: Decimal
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    waived_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
