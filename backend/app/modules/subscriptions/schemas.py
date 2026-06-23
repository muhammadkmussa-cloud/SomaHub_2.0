import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionCreate(BaseModel):
    tenant_id: uuid.UUID
    plan: str = Field(..., pattern="^(starter|professional|enterprise)$")
    status: str = Field("trialing", pattern="^(active|trialing|past_due|canceled)$")
    starts_at: datetime
    ends_at: datetime


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    plan: str
    status: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
