# SomaHub Enterprise

# Project Architecture Document (PAD)

Version: 1.0

---

# 1. Architecture Principles

SomaHub follows:

* Domain Driven Design (DDD)
* Modular Monolith Architecture
* Clean Architecture Principles
* Multi-Tenant First Design
* API-First Development
* Cloud Native Deployment

Initial deployment is a modular monolith.

Future microservices can be extracted without major rewrites.

---

# 2. High-Level Architecture

```text
React Frontend
        │
        ▼
FastAPI API Layer
        │
        ▼
Application Services
        │
        ▼
Repositories
        │
        ▼
PostgreSQL
```

Supporting Services:

```text
Redis
Supabase Storage
Gemini OCR
Stripe
Paystack
Resend
```

---

# 3. Backend Structure

```text
backend/

├── app/
│
├── core/
├── modules/
├── infrastructure/
├── workers/
├── tests/
├── scripts/
├── docs/
│
├── alembic/
│
├── main.py
├── pyproject.toml
└── .env
```

---

# 4. Core Layer

Contains application-wide functionality.

```text
core/

├── config.py
├── database.py
├── security.py
├── tenant.py
├── permissions.py
├── exceptions.py
├── logging.py
├── dependencies.py
└── constants.py
```

---

## config.py

Handles:

* Environment variables
* Secrets
* Feature flags

Uses:

```python
pydantic-settings
```

---

## database.py

Handles:

* Async engine
* Session management
* Connection pooling

Uses:

```python
SQLAlchemy 2.0
AsyncSession
```

---

## security.py

Handles:

* JWT creation
* JWT validation
* Argon2 password hashing

Uses:

```python
PyJWT
pwdlib[argon2]
```

---

## tenant.py

Handles:

* Tenant resolution
* Tenant context
* Tenant validation

Responsibilities:

```text
Extract tenant
Validate tenant
Apply tenant scope
```

---

# 5. Modules Layer

Every business feature lives inside its own module.

```text
modules/

├── auth/
├── tenants/
├── users/
├── libraries/
├── librarians/
├── borrowers/
├── books/
├── loans/
├── fines/
├── bookstore/
├── reader/
├── reviews/
├── payments/
├── notifications/
├── analytics/
├── ocr/
├── subscriptions/
├── audit/
└── admin/
```

---

# 6. Internal Module Structure

Every module follows the same pattern.

Example:

```text
books/

├── router.py
├── service.py
├── repository.py
├── models.py
├── schemas.py
├── dependencies.py
└── exceptions.py
```

---

## router.py

Contains:

```text
API Endpoints
Request Handling
Response Mapping
```

Example:

```text
GET /books
POST /books
PUT /books/{id}
DELETE /books/{id}
```

---

## service.py

Contains:

```text
Business Logic
Validation
Workflow Orchestration
```

Example:

```text
Issue Book
Return Book
Update Copies
```

---

## repository.py

Contains:

```text
Database Access
Queries
Transactions
```

Only repositories communicate directly with database models.

---

## models.py

Contains:

```text
SQLAlchemy Models
Relationships
Indexes
```

---

## schemas.py

Contains:

```text
Request Schemas
Response Schemas
Validation Rules
```

Uses:

```python
Pydantic
```

---

# 7. Authentication Module

```text
auth/

├── router.py
├── service.py
├── repository.py
├── schemas.py
├── tokens.py
└── dependencies.py
```

Features:

* Login
* Logout
* Refresh Token
* Password Reset
* Email Verification

Roles:

```text
super_admin
library_admin
librarian
reader
```

---

# 8. Books Module

Responsibilities:

* Catalog Management
* OCR Assisted Cataloging
* Copy Tracking
* Availability Tracking

Features:

```text
Create Book
Update Book
Delete Book
Search Books
Scan ISBN
```

---

# 9. Borrowers Module

Responsibilities:

* Borrower Registration
* Membership Tracking

Features:

```text
Create Borrower
Update Borrower
Borrower History
Student ID OCR
```

---

# 10. Loans Module

Responsibilities:

```text
Issue Books
Return Books
Track Due Dates
Track Status
```

States:

```text
issued
overdue
returned
lost
```

---

# 11. Fines Module

Responsibilities:

```text
Calculate Fines
Collect Fines
Generate Reports
```

Features:

```text
Daily Totals
Monthly Totals
Yearly Totals
```

---

# 12. Bookstore Module

Responsibilities:

```text
Marketplace Books
Purchases
Ownership
Catalog Search
```

Features:

```text
Browse Books
Purchase Books
Reader Library
```

---

# 13. Reader Module

Responsibilities:

```text
Reading Experience
Progress Tracking
Bookmarks
```

Features:

```text
Continue Reading
Save Progress
Track Reading Time
```

---

# 14. OCR Module

```text
ocr/

├── router.py
├── service.py
├── providers/
│
├── isbn_scanner.py
├── student_id_scanner.py
└── cover_scanner.py
```

Workflow:

```text
Upload
→ Process
→ Extract
→ Validate
→ Review
→ Save
```

---

# 15. Payment Module

```text
payments/

├── stripe.py
├── paystack.py
├── webhooks.py
├── service.py
└── repository.py
```

Payment Types:

```text
ebook_purchase
library_subscription
fine_payment
```

---

# 16. Notification Module

Providers:

```text
Resend
```

Future:

```text
SMS
Push Notifications
```

Notification Types:

```text
Password Reset
Verification
Overdue Reminder
Fine Reminder
Purchase Receipt
```

---

# 17. Analytics Module

Responsibilities:

```text
Library Analytics
Platform Analytics
Revenue Analytics
```

Recommended Tables:

```text
analytics_snapshots
revenue_snapshots
```

Store daily aggregates.

Avoid expensive live calculations.

---

# 18. Infrastructure Layer

```text
infrastructure/

├── storage/
├── email/
├── cache/
├── payments/
├── ocr/
└── monitoring/
```

---

## Storage

Provider:

```text
Supabase Storage
```

Stores:

```text
ebooks
book covers
profile images
ocr uploads
```

---

## Cache

Provider:

```text
Redis
```

Uses:

```text
JWT blacklist
Caching
Rate Limiting
Temporary Tokens
```

---

# 19. Database Architecture

Main Database:

```text
PostgreSQL
```

Provider:

```text
Neon
```

---

## Required Tenant Tables

```text
users
books
borrowers
loans
fines
notifications
subscriptions
payments
reviews
```

All include:

```sql
tenant_id UUID NOT NULL
```

---

## Row Level Security

```sql
tenant_id =
current_setting(
'app.current_tenant_id'
)::UUID
```

Mandatory for all tenant-owned tables.

---

# 20. Background Processing

Current:

```text
FastAPI BackgroundTasks
```

Future:

```text
Celery
Redis
```

Jobs:

```text
OCR
Email Sending
Reports
Notifications
```

---

# 21. Testing Architecture

```text
tests/

├── unit/
├── integration/
├── functional/
└── fixtures/
```

Tools:

```text
Pytest
HTTPX
pytest-asyncio
```

Coverage Goal:

```text
80%+
```

---

# 22. Deployment Architecture

Development:

```text
Docker Compose
```

Containers:

```text
frontend
backend
postgres
redis
```

---

Production:

```text
GitHub
    ↓
GitHub Actions
    ↓
Cloud Build
    ↓
Artifact Registry
    ↓
Cloud Run
```

Database:

```text
Neon PostgreSQL
```

Storage:

```text
Supabase Storage
```

---

# 23. Security Architecture

Application Security:

```text
JWT
Argon2
RBAC
RLS
Audit Logs
Rate Limiting
```

Cloud Security:

```text
HTTPS
Cloud Run IAM
Secrets Manager
```

VPS Security (Optional):

```text
Nginx
UFW
Fail2Ban
```

---

# 24. Logging & Monitoring

Tools:

```text
OpenTelemetry
Cloud Logging
Cloud Monitoring
```

Metrics:

```text
Response Time
Error Rate
Revenue
Queue Depth
User Activity
```

---

# 25. Recommended Development Order

Phase 1

* Authentication
* Tenants
* Users
* Libraries

Phase 2

* Books
* Borrowers
* Loans
* Fines

Phase 3

* OCR
* Notifications
* Analytics

Phase 4

* Digital Bookstore
* Reader Module
* Reviews

Phase 5

* Payments
* Subscriptions
* Super Admin Dashboard

Phase 6

* Monitoring
* Security Hardening
* Cloud Run Deployment
