from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fines.models import Fine


class FineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, fine_id: UUID, tenant_id: UUID | None = None) -> Optional[Fine]:
        stmt = select(Fine).where(Fine.id == fine_id)
        if tenant_id:
            stmt = stmt.where(Fine.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID | None = None,
        status: str | None = None,
        borrower_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Fine]:
        stmt = select(Fine)
        if tenant_id:
            stmt = stmt.where(Fine.tenant_id == tenant_id)
        if status:
            stmt = stmt.where(Fine.status == status)
        if borrower_id:
            stmt = stmt.where(Fine.borrower_id == borrower_id)
        result = await self.session.execute(
            stmt.order_by(Fine.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, tenant_id: UUID, **data) -> Fine:
        fine = Fine(tenant_id=tenant_id, **data)
        self.session.add(fine)
        await self.session.flush()
        await self.session.refresh(fine)
        return fine

    async def pay(self, fine: Fine, amount: Decimal) -> Fine:
        fine.paid_amount = fine.paid_amount + amount
        if fine.paid_amount >= fine.amount:
            fine.paid_amount = fine.amount
            fine.status = "paid"
            fine.paid_at = datetime.now(timezone.utc)
        self.session.add(fine)
        await self.session.flush()
        await self.session.refresh(fine)
        return fine

    async def waive(self, fine: Fine) -> Fine:
        fine.status = "waived"
        fine.waived_at = datetime.now(timezone.utc)
        self.session.add(fine)
        await self.session.flush()
        await self.session.refresh(fine)
        return fine
