# Security

## Tenant isolation

- All tenant-scoped repository queries filter by `tenant_id` for non-super-admin callers.
- Cross-tenant access attempts return `404` (not `403`) to avoid leaking resource existence.
- Tests: `backend/tests/test_tenant_isolation.py`

## Authentication

- Passwords hashed with Argon2 (`pwdlib`)
- JWT access tokens include `jti` for blacklist on logout
- Refresh tokens stored in Redis with rotation
- Rate limiting on login, signup, forgot-password (10 req/min per IP)

## Webhooks

- Stripe: signature verified via `stripe.Webhook.construct_event`
- Paystack: HMAC-SHA512 signature verification
- Unsigned webhooks rejected in staging/production

## Pre-production checklist

- [ ] `SECRET_KEY` set to a strong random value (64+ chars)
- [ ] `APP_ENV=production` and `DEBUG=false`
- [ ] `COOKIE_SECURE=true` (automatic when `APP_ENV=production`)
- [ ] CORS locked to production frontend origin
- [ ] `STRIPE_WEBHOOK_SECRET` and `PAYSTACK_SECRET_KEY` configured
- [ ] Redis reachable (no in-memory fallback in production)
- [ ] PostgreSQL backups configured
- [ ] Run `uv pip audit` and `npm audit`
- [ ] Review `test_tenant_isolation.py` passes in CI

## Dependency audit

```bash
cd backend && uv pip audit
cd frontend && npm audit
```

## Reporting vulnerabilities

Contact the platform administrator. Do not open public issues for security findings.
