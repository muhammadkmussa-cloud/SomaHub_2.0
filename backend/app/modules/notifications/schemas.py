import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    category: str = Field("system", max_length=50)
    channel: str = Field("in_app", max_length=30)
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)


class NotificationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    category: str
    channel: str
    title: str
    message: str
    status: str
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
