# SomaHub Backend

FastAPI multi-tenant library management API.

## Setup

```bash
cd backend
uv sync --all-groups
cp .env.example .env
# Edit .env — set SECRET_KEY at minimum
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
APP_ENV=testing SECRET_KEY=test-key uv run pytest tests/ -v --cov=app
```

## Migrations

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
uv run alembic downgrade -1
```

## Key environment variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key (required in staging/production) |
| `DATABASE_URL` | PostgreSQL async URL |
| `REDIS_URL` | Redis for tokens and rate limiting |
| `STRIPE_SECRET_KEY` | Stripe checkout and webhooks |
| `PAYSTACK_SECRET_KEY` | Paystack checkout and webhooks |
| `RESEND_API_KEY` | Transactional email |

See [.env.example](.env.example) for the full list.

## Payment smoke test

```bash
uv run python scripts/smoke_test_payments.py
```
