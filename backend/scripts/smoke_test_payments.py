#!/usr/bin/env python3
"""Manual smoke test for payment checkout and webhooks (dev/test mode)."""

import asyncio
import os
import sys

import httpx

BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")
EMAIL = os.getenv("SMOKE_EMAIL", "librarian@test.com")
PASSWORD = os.getenv("SMOKE_PASSWORD", "password123")


async def main() -> int:
    async with httpx.AsyncClient(base_url=BASE, timeout=30.0) as client:
        login = await client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD})
        if login.status_code != 200:
            print("Login failed:", login.text)
            return 1
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        stripe = await client.post(
            "/payments/checkout/stripe",
            headers=headers,
            json={
                "payment_type": "subscription",
                "amount": 29.99,
                "currency": "USD",
                "success_url": "http://localhost:5173/billing/success",
                "cancel_url": "http://localhost:5173/billing/cancel",
                "metadata": {"plan": "pro"},
            },
        )
        print("Stripe checkout:", stripe.status_code, stripe.json())

        paystack = await client.post(
            "/payments/checkout/paystack",
            headers=headers,
            json={
                "payment_type": "fine",
                "amount": 1000.0,
                "currency": "NGN",
                "success_url": "http://localhost:5173/billing/success",
                "cancel_url": "http://localhost:5173/billing/cancel",
                "metadata": {},
            },
        )
        print("Paystack checkout:", paystack.status_code, paystack.json())

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
