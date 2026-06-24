# SomaHub Enterprise

# Software Requirements Specification (SRS)

Version: 1.0

---

# 1. Introduction

## 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for SomaHub Enterprise.

The document serves as the primary reference for:

* Product Development
* Backend Development
* Frontend Development
* Database Design
* Testing
* Deployment

---

## 1.2 Product Scope

SomaHub is a multi-tenant Library Management and Digital Reading Platform that enables educational institutions to:

* Manage physical library inventories
* Manage borrowers
* Process loans and returns
* Collect fines
* Manage subscriptions
* Sell digital books
* Support in-platform ebook reading
* Generate reports and analytics

---

## 1.3 Intended Users

### Platform Users

* Super Admin

### Tenant Users

* Library Administrator
* Librarian
* Reader

---

# 2. System Overview

## 2.1 System Context

```text
React Frontend
        │
        ▼
FastAPI Backend
        │
 ┌──────┼──────┐
 ▼      ▼      ▼
PostgreSQL Redis Storage
```

External Services:

* Stripe
* Paystack
* Gemini OCR
* Resend
* Supabase Storage

---

# 3. Functional Requirements

# 3.1 Authentication Module

## FR-AUTH-001

The system shall allow platform users to authenticate.

---

## FR-AUTH-002

The system shall allow tenant users to authenticate.

---

## FR-AUTH-003

The system shall issue JWT access tokens.

---

## FR-AUTH-004

The system shall issue refresh tokens.

---

## FR-AUTH-005

The system shall support password reset.

---

## FR-AUTH-006

The system shall support email verification.

---

## FR-AUTH-007

The system shall support logout.

---

# 3.2 Tenant Management

## FR-TENANT-001

The system shall allow super admins to create tenants.

---

## FR-TENANT-002

The system shall allow super admins to suspend tenants.

---

## FR-TENANT-003

The system shall isolate tenant data using PostgreSQL RLS.

---

## FR-TENANT-004

The system shall support subscription plans.

---

# 3.3 User Management

## FR-USER-001

Library administrators shall create librarian accounts.

---

## FR-USER-002

Library administrators shall deactivate users.

---

## FR-USER-003

Library administrators shall assign roles.

---

## FR-USER-004

The system shall maintain user activity logs.

---

# 3.4 Book Management

## FR-BOOK-001

The system shall allow manual book creation.

---

## FR-BOOK-002

The system shall support ISBN scanning.

---

## FR-BOOK-003

The system shall support OCR-assisted book creation.

---

## FR-BOOK-004

The system shall allow book editing.

---

## FR-BOOK-005

The system shall allow book deletion.

---

## FR-BOOK-006

The system shall track available copies.

---

## FR-BOOK-007

The system shall support search by:

* Title
* Author
* ISBN

---

# 3.5 Borrower Management

## FR-BORROWER-001

The system shall allow borrower registration.

---

## FR-BORROWER-002

The system shall support student ID scanning.

---

## FR-BORROWER-003

The system shall store borrower history.

---

## FR-BORROWER-004

The system shall support borrower suspension.

---

# 3.6 Loan Management

## FR-LOAN-001

The system shall issue books.

---

## FR-LOAN-002

The system shall process returns.

---

## FR-LOAN-003

The system shall track due dates.

---

## FR-LOAN-004

The system shall automatically mark overdue loans.

---

## FR-LOAN-005

The system shall generate loan receipts.

---

# 3.7 Fine Management

## FR-FINE-001

The system shall calculate fines.

---

## FR-FINE-002

The system shall record fine payments.

---

## FR-FINE-003

The system shall support fine waivers.

---

## FR-FINE-004

The system shall generate fine reports.

---

# 3.8 OCR Module

## FR-OCR-001

The system shall support student ID scanning.

---

## FR-OCR-002

The system shall support ISBN scanning.

---

## FR-OCR-003

The system shall support book cover scanning.

---

## FR-OCR-004

The system shall require user review before saving OCR results.

---

# 3.9 Digital Marketplace

## FR-MARKET-001

The system shall display published ebooks.

---

## FR-MARKET-002

The system shall support ebook purchases.

---

## FR-MARKET-003

The system shall maintain purchase history.

---

## FR-MARKET-004

The system shall support ratings and reviews.

---

# 3.10 Reader Module

## FR-READ-001

The system shall allow ebook reading within the platform.

---

## FR-READ-002

The system shall save reading progress.

---

## FR-READ-003

The system shall support bookmarks.

---

## FR-READ-004

The system shall support favorites.

---

# 3.11 Payment Module

## FR-PAY-001

The system shall integrate Stripe.

---

## FR-PAY-002

The system shall integrate Paystack.

---

## FR-PAY-003

The system shall support payment webhooks.

---

## FR-PAY-004

The system shall generate payment records.

---

# 3.12 Notifications

## FR-NOTIFY-001

The system shall send email notifications.

---

## FR-NOTIFY-002

The system shall send password reset emails.

---

## FR-NOTIFY-003

The system shall send overdue reminders.

---

## FR-NOTIFY-004

The system shall send purchase confirmations.

---

# 3.13 Analytics

## FR-ANALYTICS-001

The system shall display borrowing statistics.

---

## FR-ANALYTICS-002

The system shall display revenue statistics.

---

## FR-ANALYTICS-003

The system shall display platform metrics.

---

# 3.14 Audit Logging

## FR-AUDIT-001

The system shall record security events.

---

## FR-AUDIT-002

The system shall record administrative actions.

---

## FR-AUDIT-003

The system shall retain audit logs.

---

# 4. Non-Functional Requirements

## NFR-001 Performance

API response time:

≤ 500 ms for normal requests.

---

## NFR-002 Scalability

The platform shall support:

* 1000+ tenants
* 100,000+ users

---

## NFR-003 Availability

Target uptime:

99.9%

---

## NFR-004 Security

Authentication:

* JWT
* Argon2

Authorization:

* RBAC
* RLS

---

## NFR-005 Accessibility

Minimum:

WCAG AA

---

## NFR-006 Maintainability

Architecture:

* Modular Monolith
* Domain-Based Modules

---

## NFR-007 Observability

The platform shall support:

* Logging
* Metrics
* Tracing

---

# 5. API Requirements

Base URL:

```text
/api/v1
```

Modules:

```text
/auth
/platform
/users
/books
/borrowers
/loans
/fines
/payments
/notifications
/bookstore
/reader
/analytics
/ocr
```

Response Format:

```json
{
  "success": true,
  "message": "Operation completed",
  "data": {}
}
```

Error Format:

```json
{
  "success": false,
  "message": "Validation error",
  "errors": []
}
```

---

# 6. Database Requirements

Database:

PostgreSQL

Provider:

Neon

ORM:

SQLAlchemy 2.0

Migration:

Alembic

Requirements:

* UUID primary keys
* Audit timestamps
* Foreign key constraints
* Row Level Security

---

# 7. Infrastructure Requirements

Containerization:

* Docker
* Docker Compose

CI/CD:

* GitHub Actions
* Cloud Build

Deployment:

* Google Cloud Run

Container Registry:

* Artifact Registry

---

# 8. Security Requirements

Application Security:

* Argon2 Password Hashing
* JWT Authentication
* RBAC
* Input Validation
* Rate Limiting

Infrastructure Security:

* HTTPS
* Secret Management

VPS Security (Optional):

* UFW
* Fail2Ban
* Nginx

---

# 9. Testing Requirements

Testing Framework:

* Pytest
* HTTPX
* pytest-asyncio

Minimum Coverage:

80%

Required Tests:

* Unit Tests
* Integration Tests
* API Tests
* Authentication Tests
* Payment Tests

---

# 10. Acceptance Criteria

The system shall be considered production-ready when:

* Multi-tenancy functions correctly
* RLS policies are enforced
* Authentication passes security testing
* OCR workflows function correctly
* Payments process successfully
* Notifications are delivered
* Analytics dashboards are operational
* Automated tests pass
* Cloud Run deployment succeeds
* Security requirements are satisfied
