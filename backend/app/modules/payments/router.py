import hashlib
import hmac
import json
import logging
from typing import List
from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.payments.checkout import CheckoutService
from app.modules.payments.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    PaymentResponse,
)
from app.modules.payments.service import PaymentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])


def _require_webhook_secret_in_production(secret: str, provider: str) -> None:
    if settings.APP_ENV in ("staging", "production") and not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{provider} webhook secret is not configured.",
        )


@router.get(
    "",
    response_model=List[PaymentResponse],
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def list_payments(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = 100,
    offset: int = 0,
):
    service = PaymentService(db)
    tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
    return await service.list_payments(tenant_id=tenant_id, limit=limit, offset=offset)


@router.post("/checkout/stripe", response_model=CheckoutResponse)
async def stripe_checkout(
    data: CheckoutRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    service = CheckoutService(db)
    tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
    result = await service.create_stripe_checkout(
        UUID(current_user.user_id), tenant_id, data
    )
    await db.commit()
    return result


@router.post("/checkout/paystack", response_model=CheckoutResponse)
async def paystack_checkout(
    data: CheckoutRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    from app.modules.auth.repository import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(current_user.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    service = CheckoutService(db)
    tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
    result = await service.create_paystack_checkout(
        UUID(current_user.user_id), tenant_id, data, user.email
    )
    await db.commit()
    return result


@router.post("/webhook/stripe", status_code=status.HTTP_200_OK, include_in_schema=False)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    stripe_signature: str | None = Header(None, alias="stripe-signature"),
):
    payload = await request.body()

    if not payload:
        return {"status": "skipped", "reason": "empty payload"}

    _require_webhook_secret_in_production(settings.STRIPE_WEBHOOK_SECRET, "Stripe")

    if settings.APP_ENV in ("staging", "production"):
        if not stripe_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature header.",
            )
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as exc:
            logger.warning("Stripe webhook verification failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stripe signature verification failed.",
            ) from exc
    elif settings.STRIPE_WEBHOOK_SECRET and stripe_signature:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stripe signature verification failed.",
            ) from exc
    else:
        event = json.loads(payload.decode("utf-8"))

    event_type = (
        event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
    )
    event_data = (
        event.get("data", {}) if isinstance(event, dict) else getattr(event, "data", {})
    )
    obj = event_data.get("object", {})

    logger.info("Stripe webhook received: type=%s", event_type)

    if event_type == "checkout.session.completed":
        metadata = obj.get("metadata", {})
        reference = obj.get("id") or metadata.get("reference")

        if reference:
            service = PaymentService(db)
            metadata["provider"] = "stripe"
            metadata["amount"] = obj.get("amount_total", 0) / 100.0
            metadata["currency"] = obj.get("currency", "USD").upper()

            await service.fulfill_payment(reference, metadata)
            await db.commit()
            logger.info("Stripe payment fulfilled: reference=%s", reference)

    return {"status": "success"}


@router.post(
    "/webhook/paystack", status_code=status.HTTP_200_OK, include_in_schema=False
)
async def paystack_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_paystack_signature: str | None = Header(None, alias="x-paystack-signature"),
):
    payload = await request.body()

    if not payload:
        return {"status": "skipped", "reason": "empty payload"}

    _require_webhook_secret_in_production(settings.PAYSTACK_SECRET_KEY, "Paystack")

    if settings.APP_ENV in ("staging", "production"):
        if not x_paystack_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Paystack signature header.",
            )
        hash_value = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()
        if not hmac.compare_digest(hash_value, x_paystack_signature):
            logger.warning("Paystack webhook signature verification failed")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paystack signature verification failed",
            )
    elif settings.PAYSTACK_SECRET_KEY and x_paystack_signature:
        hash_value = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
            payload,
            hashlib.sha512,
        ).hexdigest()
        if not hmac.compare_digest(hash_value, x_paystack_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Paystack signature verification failed",
            )

    try:
        event = json.loads(payload.decode("utf-8"))
    except json.JSONDecodeError:
        return {"status": "skipped", "reason": "invalid json"}

    event_type = event.get("event")
    logger.info("Paystack webhook received: event=%s", event_type)

    if event_type == "charge.success":
        data = event.get("data", {})
        reference = data.get("reference")
        metadata = data.get("metadata", {})

        if reference:
            service = PaymentService(db)
            metadata["provider"] = "paystack"
            metadata["amount"] = data.get("amount", 0) / 100.0
            metadata["currency"] = data.get("currency", "NGN").upper()

            await service.fulfill_payment(reference, metadata)
            await db.commit()
            logger.info("Paystack payment fulfilled: reference=%s", reference)

    return {"status": "success"}
