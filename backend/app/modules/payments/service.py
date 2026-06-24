from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import PaymentCreate


class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PaymentRepository(session)

    async def create_payment(self, data: PaymentCreate) -> Payment:
        # Check if already exists
        existing = await self.repo.get_by_reference(data.reference)
        if existing:
            return existing
        return await self.repo.create(**data.model_dump())

    async def list_payments(
        self, tenant_id: UUID | None = None, limit: int = 100, offset: int = 0
    ):
        return await self.repo.list(tenant_id, limit, offset)

    async def get_payment_by_ref(self, reference: str) -> Payment | None:
        return await self.repo.get_by_reference(reference)

    async def fulfill_payment(self, reference: str, metadata: dict) -> Payment:
        payment = await self.repo.get_by_reference(reference)
        if payment and payment.status == "completed":
            return payment

        if not payment:
            # Create a payment record on the fly
            payment = await self.repo.create(
                tenant_id=UUID(metadata["tenant_id"])
                if "tenant_id" in metadata and metadata["tenant_id"]
                else None,
                provider=metadata.get("provider", "stripe"),
                reference=reference,
                amount=float(metadata.get("amount", 0)),
                currency=metadata.get("currency", "USD"),
                status="completed",
                payment_type=metadata.get("payment_type"),
            )
        else:
            payment = await self.repo.update(payment, status="completed")

        payment_type = payment.payment_type

        # Fulfill depending on payment type
        if payment_type == "ebook_purchase":
            from app.modules.ebook_purchases.models import EbookPurchase

            user_id = UUID(metadata["user_id"])
            ebook_id = UUID(metadata["ebook_id"])

            # Check if purchase already exists
            from sqlalchemy import select

            purchase_stmt = select(EbookPurchase).where(
                EbookPurchase.user_id == user_id, EbookPurchase.ebook_id == ebook_id
            )
            res = await self.session.execute(purchase_stmt)
            existing_purchase = res.scalar_one_or_none()

            if not existing_purchase:
                new_purchase = EbookPurchase(
                    user_id=user_id,
                    ebook_id=ebook_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    payment_id=payment.id,
                )
                self.session.add(new_purchase)

        elif payment_type == "fine":
            from app.modules.fines.models import Fine

            fine_id = UUID(metadata["fine_id"])
            fine_stmt = select(Fine).where(Fine.id == fine_id)
            res = await self.session.execute(fine_stmt)
            fine = res.scalar_one_or_none()
            if fine:
                from datetime import datetime, timezone

                fine.status = "paid"
                fine.paid_amount = fine.amount
                fine.paid_at = datetime.now(timezone.utc)
                self.session.add(fine)

        elif payment_type == "subscription":
            from app.modules.subscriptions.models import Subscription
            from app.modules.auth.models import Tenant
            from datetime import datetime, timedelta, timezone

            tenant_id = UUID(metadata["tenant_id"])
            plan = metadata.get("plan", "starter")

            # Update tenant plan
            tenant_stmt = select(Tenant).where(Tenant.id == tenant_id)
            res = await self.session.execute(tenant_stmt)
            tenant = res.scalar_one_or_none()
            if tenant:
                tenant.plan = plan
                self.session.add(tenant)

            # Create or update subscription
            sub_stmt = select(Subscription).where(Subscription.tenant_id == tenant_id)
            res = await self.session.execute(sub_stmt)
            sub = res.scalar_one_or_none()

            now = datetime.now(timezone.utc)
            ends = now + timedelta(days=30)  # default 30 days billing cycle

            if sub:
                sub.plan = plan
                sub.status = "active"
                sub.starts_at = now
                sub.ends_at = ends
                self.session.add(sub)
            else:
                new_sub = Subscription(
                    tenant_id=tenant_id,
                    plan=plan,
                    status="active",
                    starts_at=now,
                    ends_at=ends,
                )
                self.session.add(new_sub)

        await self.session.flush()
        return payment
