from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, payment_id: UUID, tenant_id: UUID | None = None) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.id == payment_id)
        if tenant_id:
            stmt = stmt.where(Payment.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_reference(
        self, reference: str, tenant_id: UUID | None = None
    ) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.reference == reference)
        if tenant_id:
            stmt = stmt.where(Payment.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Payment]:
        stmt = select(Payment)
        if tenant_id:
            stmt = stmt.where(Payment.tenant_id == tenant_id)
        stmt = stmt.order_by(Payment.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **data) -> Payment:
        payment = Payment(**data)
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def update(self, payment: Payment, **data) -> Payment:
        for key, value in data.items():
            if value is not None:
                setattr(payment, key, value)
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment
