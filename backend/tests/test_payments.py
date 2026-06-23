"""
Payments API tests.
"""

import hashlib
import hmac
import json

import pytest


@pytest.mark.asyncio
async def test_list_payments(async_client, admin_headers):
    """GET /api/v1/payments → list of payments."""
    response = await async_client.get("/api/v1/payments", headers=admin_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_payments_reader_forbidden(async_client, auth_headers):
    """GET /api/v1/payments → 403 for reader."""
    response = await async_client.get("/api/v1/payments", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_stripe_checkout_mock(async_client, auth_headers):
    """POST /api/v1/payments/checkout/stripe → mock checkout URL without API key."""
    response = await async_client.post(
        "/api/v1/payments/checkout/stripe",
        json={
            "payment_type": "ebook_purchase",
            "amount": 9.99,
            "currency": "USD",
            "success_url": "http://localhost:5173/success",
            "cancel_url": "http://localhost:5173/cancel",
            "metadata": {"ebook_id": "00000000-0000-0000-0000-000000000001"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "stripe"
    assert "checkout_url" in data
    assert data["reference"].startswith("stripe_")


@pytest.mark.asyncio
async def test_paystack_checkout_mock(async_client, auth_headers):
    """POST /api/v1/payments/checkout/paystack → mock checkout URL without API key."""
    response = await async_client.post(
        "/api/v1/payments/checkout/paystack",
        json={
            "payment_type": "fine",
            "amount": 10.0,
            "currency": "NGN",
            "success_url": "http://localhost:5173/success",
            "cancel_url": "http://localhost:5173/cancel",
            "metadata": {"fine_id": "00000000-0000-0000-0000-000000000002"},
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "paystack"
    assert data["reference"].startswith("paystack_")


@pytest.mark.asyncio
async def test_stripe_webhook(async_client):
    """POST /api/v1/payments/webhook/stripe → 200 (empty payload handled gracefully)."""
    response = await async_client.post(
        "/api/v1/payments/webhook/stripe",
        json={},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_paystack_webhook(async_client):
    """POST /api/v1/payments/webhook/paystack → 200."""
    response = await async_client.post(
        "/api/v1/payments/webhook/paystack",
        json={},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_stripe_webhook_idempotent(async_client, db_session, test_user):
    """Duplicate Stripe webhook fulfillment is idempotent."""
    from app.modules.payments.service import PaymentService
    from app.modules.payments.schemas import PaymentCreate

    service = PaymentService(db_session)
    reference = "cs_test_idempotent_123"
    metadata = {
        "user_id": str(test_user.id),
        "ebook_id": "00000000-0000-0000-0000-000000000099",
        "payment_type": "ebook_purchase",
        "provider": "stripe",
        "amount": 0,
        "currency": "USD",
    }
    await service.create_payment(
        PaymentCreate(
            provider="stripe",
            reference=reference,
            amount=0,
            currency="USD",
            status="pending",
            payment_type="ebook_purchase",
        )
    )
    await db_session.commit()

    await service.fulfill_payment(reference, metadata)
    await db_session.commit()
    payment1 = await service.get_payment_by_ref(reference)

    await service.fulfill_payment(reference, metadata)
    await db_session.commit()
    payment2 = await service.get_payment_by_ref(reference)

    assert payment1.id == payment2.id
    assert payment2.status == "completed"


@pytest.mark.asyncio
async def test_paystack_webhook_invalid_signature(monkeypatch):
    """Invalid Paystack signature returns 400 when secret is configured."""
    from httpx import ASGITransport, AsyncClient
    from app.main import app
    from app.core.config import settings

    monkeypatch.setattr(settings, "APP_ENV", "staging")
    monkeypatch.setattr(settings, "PAYSTACK_SECRET_KEY", "test_secret_key")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = json.dumps({"event": "charge.success", "data": {}}).encode()
        response = await client.post(
            "/api/v1/payments/webhook/paystack",
            content=payload,
            headers={"x-paystack-signature": "invalid"},
        )
        assert response.status_code == 400
