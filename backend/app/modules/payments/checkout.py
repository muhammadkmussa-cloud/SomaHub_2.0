"""Checkout session creation for Stripe and Paystack."""

from uuid import UUID, uuid4

import httpx
import stripe
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.payments.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    PaymentCreate,
)
from app.modules.payments.service import PaymentService


class CheckoutService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payments = PaymentService(session)

    async def create_stripe_checkout(
        self,
        user_id: UUID,
        tenant_id: UUID | None,
        data: CheckoutRequest,
    ) -> CheckoutResponse:
        metadata = {
            **data.metadata,
            "user_id": str(user_id),
            "payment_type": data.payment_type,
        }
        if tenant_id:
            metadata["tenant_id"] = str(tenant_id)

        reference = f"stripe_{uuid4().hex}"

        if settings.APP_ENV == "testing" or not settings.STRIPE_SECRET_KEY:
            await self.payments.create_payment(
                PaymentCreate(
                    tenant_id=tenant_id,
                    provider="stripe",
                    reference=reference,
                    amount=data.amount,
                    currency=data.currency.upper(),
                    status="pending",
                    payment_type=data.payment_type,
                )
            )
            return CheckoutResponse(
                checkout_url=f"{data.success_url}?reference={reference}&mock=1",
                reference=reference,
                provider="stripe",
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            mode="payment",
            success_url=data.success_url,
            cancel_url=data.cancel_url,
            line_items=[
                {
                    "price_data": {
                        "currency": data.currency.lower(),
                        "unit_amount": int(data.amount * 100),
                        "product_data": {"name": f"SomaHub {data.payment_type}"},
                    },
                    "quantity": 1,
                }
            ],
            metadata=metadata,
        )
        reference = session.id

        await self.payments.create_payment(
            PaymentCreate(
                tenant_id=tenant_id,
                provider="stripe",
                reference=reference,
                amount=data.amount,
                currency=data.currency.upper(),
                status="pending",
                payment_type=data.payment_type,
            )
        )

        return CheckoutResponse(
            checkout_url=session.url or data.success_url,
            reference=reference,
            provider="stripe",
        )

    async def create_paystack_checkout(
        self,
        user_id: UUID,
        tenant_id: UUID | None,
        data: CheckoutRequest,
        email: str,
    ) -> CheckoutResponse:
        metadata = {
            **data.metadata,
            "user_id": str(user_id),
            "payment_type": data.payment_type,
        }
        if tenant_id:
            metadata["tenant_id"] = str(tenant_id)

        reference = f"paystack_{uuid4().hex}"

        if settings.APP_ENV == "testing" or not settings.PAYSTACK_SECRET_KEY:
            await self.payments.create_payment(
                PaymentCreate(
                    tenant_id=tenant_id,
                    provider="paystack",
                    reference=reference,
                    amount=data.amount,
                    currency=data.currency.upper(),
                    status="pending",
                    payment_type=data.payment_type,
                )
            )
            return CheckoutResponse(
                checkout_url=f"{data.success_url}?reference={reference}&mock=1",
                reference=reference,
                provider="paystack",
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.paystack.co/transaction/initialize",
                headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
                json={
                    "email": email,
                    "amount": int(data.amount * 100),
                    "currency": data.currency.upper(),
                    "callback_url": data.success_url,
                    "metadata": metadata,
                },
                timeout=30.0,
            )

        if response.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Paystack checkout initialization failed.",
            )

        body = response.json()
        if not body.get("status"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=body.get("message", "Paystack error"),
            )

        paystack_data = body["data"]
        reference = paystack_data["reference"]

        await self.payments.create_payment(
            PaymentCreate(
                tenant_id=tenant_id,
                provider="paystack",
                reference=reference,
                amount=data.amount,
                currency=data.currency.upper(),
                status="pending",
                payment_type=data.payment_type,
            )
        )

        return CheckoutResponse(
            checkout_url=paystack_data["authorization_url"],
            reference=reference,
            provider="paystack",
        )
