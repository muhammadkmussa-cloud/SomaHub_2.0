import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    tenant_id: Optional[uuid.UUID] = None
    provider: str = Field(..., max_length=50)
    reference: str = Field(..., max_length=255)
    amount: float = Field(..., ge=0.0)
    currency: str = Field("USD", max_length=10)
    status: str = Field("pending", max_length=50)
    payment_type: str = Field(..., max_length=50)


class PaymentUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)


class PaymentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    provider: str
    reference: str
    amount: float
    currency: str
    status: str
    payment_type: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CheckoutRequest(BaseModel):
    payment_type: str = Field(..., pattern="^(subscription|fine|ebook_purchase)$")
    amount: float = Field(..., ge=0.0)
    currency: str = Field("USD", max_length=10)
    success_url: str
    cancel_url: str
    metadata: dict = Field(default_factory=dict)


class CheckoutResponse(BaseModel):
    checkout_url: str
    reference: str
    provider: str
