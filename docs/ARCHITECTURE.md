# Architecture

## Overview

SomaHub is a multi-tenant SaaS platform combining physical library circulation with a digital ebook storefront.

```
Client (React) → FastAPI → PostgreSQL
                      ↘ Redis (tokens, rate limits)
                      ↘ Stripe / Paystack (payments)
                      ↘ Resend (email)
```

## Multi-tenancy

- Each **library institution** is a `Tenant`.
- Tenant-scoped data (books, borrowers, loans, fines) includes `tenant_id` on every row.
- JWT access tokens carry `tenant_id`; request context stores it via `ContextVar`.
- **Super admin** users have `tenant_id = null` and can access platform-wide data.

## Ebooks (platform-global)

Ebooks are **not** tenant-scoped — they form a shared marketplace catalog. Purchases, favorites, bookmarks, and reading progress are **user-scoped**.

## RBAC

| Role | Scope |
|------|-------|
| `reader` | Bookstore, own purchases |
| `librarian` | Circulation within tenant |
| `library_admin` | Full tenant management + analytics |
| `super_admin` | All tenants, platform admin |

## Subscription enforcement

- Each tenant has a `Subscription` (starter / pro / enterprise).
- Write operations require active or trialing subscription.
- `past_due` blocks writes; reads remain allowed.
- Plan limits defined in `app/core/subscription.py`.

## Modules

| Module | Purpose |
|--------|---------|
| auth | Login, signup, JWT, email verify |
| tenants | Super-admin tenant CRUD |
| books / borrowers / loans / fines | Physical circulation |
| ebooks / purchases / favorites | Digital bookstore |
| payments | Stripe + Paystack checkout and webhooks |
| subscriptions | Tenant billing state |
| analytics | Dashboard aggregates |
| notifications | User notifications |

## Database migrations

Alembic migrations live in `backend/alembic/versions/`. Always run `alembic upgrade head` before starting the API.
