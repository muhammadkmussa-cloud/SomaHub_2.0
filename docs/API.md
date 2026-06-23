# API Overview

Base URL: `/api/v1`

Interactive docs (development): `http://localhost:8000/docs`

## Authentication

1. `POST /auth/login` — returns `access_token`, sets HTTP-only refresh cookie
2. Include `Authorization: Bearer <access_token>` on protected routes
3. `POST /auth/refresh-cookie` — refresh access token from cookie
4. `POST /auth/logout` — revokes refresh token and blacklists access token

## Signup

- `POST /auth/signup/reader` — platform reader account
- `POST /auth/signup/library` — creates tenant + library admin

## Circulation (librarian+)

| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/books` | Catalog |
| POST | `/book-copies` | Add copy |
| GET/POST | `/borrowers` | Borrower registry |
| GET/POST | `/loans` | Issue loans |
| POST | `/loans/{id}/return` | Return book |
| GET/POST | `/fines` | Fine management |

## Digital bookstore

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ebooks` | Catalog (published) |
| POST | `/ebook-purchases/checkout-free` | Free ebook |
| GET | `/ebook-purchases/my-library` | Owned ebooks |
| GET/POST | `/favorites` | Favorites |

## Payments

| Method | Path | Description |
|--------|------|-------------|
| POST | `/payments/checkout/stripe` | Stripe Checkout session |
| POST | `/payments/checkout/paystack` | Paystack initialize |
| POST | `/payments/webhook/stripe` | Stripe webhook |
| POST | `/payments/webhook/paystack` | Paystack webhook |

## Admin

| Method | Path | Role |
|--------|------|------|
| GET | `/tenants` | super_admin |
| GET | `/analytics/dashboard` | library_admin+ |
| GET/PATCH | `/users/me` | authenticated |

## Error format

```json
{
  "success": false,
  "message": "Human-readable error",
  "errors": []
}
```

## Status codes

- `401` — authentication required
- `403` — permission denied or tenant suspended
- `402` — subscription required
- `429` — rate limit exceeded
