import logging

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DBSession
from app.core.exceptions import PermissionDeniedError
from app.core.permissions import UserRole, require_role
from app.modules.audit.schemas import AuditLogListResponse, AuditLogResponse
from app.modules.audit.service import AuditService

logger = logging.getLogger("somahub.audit")

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    resource_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
):
    if current_user.role != UserRole.SUPER_ADMIN.value:
        raise PermissionDeniedError()

    service = AuditService(db)
    entries, total = await service.list(
        page=page,
        page_size=page_size,
        resource_type=resource_type,
        action=action,
    )
    return AuditLogListResponse(
        data=[AuditLogResponse.model_validate(e) for e in entries],
        total=total,
        page=page,
        page_size=page_size,
    )
