from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    tenant_id: UUID | None
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    details: str | None
    ip_address: str | None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    success: bool = True
    message: str = "Audit logs retrieved successfully"
    data: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
