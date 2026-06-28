from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog
from app.modules.audit.repository import AuditLogRepository


class AuditService:
    def __init__(self, session: AsyncSession):
        self.repo = AuditLogRepository(session)

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: str | None = None,
        user_id: UUID | None = None,
        tenant_id: UUID | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        return await self.repo.create(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            user_id=user_id,
            tenant_id=tenant_id,
            ip_address=ip_address,
        )

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        resource_type: str | None = None,
        action: str | None = None,
        tenant_id: UUID | None = None,
    ) -> tuple[list[AuditLog], int]:
        return await self.repo.list(
            page=page,
            page_size=page_size,
            resource_type=resource_type,
            action=action,
            tenant_id=tenant_id,
        )
