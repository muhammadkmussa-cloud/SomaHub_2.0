# SomaHub Enterprise API Specification

Version: 1.0

---

# 1. API Overview

## Base URL

```http
/api/v1
```

## Authentication

Authentication uses JWT Access Tokens.

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

---

# 2. API Standards

## Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {}
}
```

## Error Response

```json
{
  "success": false,
  "message": "Validation error",
  "errors": []
}
```

---

# 3. Authentication API

## Login

### Request

```http
POST /auth/login
```

### Request Body

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

### Response

```json
{
  "access_token": "jwt",
  "refresh_token": "jwt",
  "token_type": "bearer"
}
```

---

## Refresh Token

```http
POST /auth/refresh
```

### Request

```json
{
  "refresh_token": "jwt"
}
```

---

## Logout

```http
POST /auth/logout
```

---

## Forgot Password

```http
POST /auth/forgot-password
```

### Request

```json
{
  "email": "user@example.com"
}
```

---

## Reset Password

```http
POST /auth/reset-password
```

### Request

```json
{
  "token": "reset_token",
  "new_password": "password"
}
```

---

# 4. Platform Admin API

Base:

```http
/platform
```

---

## Create Tenant

```http
POST /platform/tenants
```

### Permission

```text
super_admin
```

### Request

```json
{
  "name": "Mombasa University Library",
  "slug": "mombasa-university",
  "email": "admin@library.com",
  "plan": "professional"
}
```

---

## List Tenants

```http
GET /platform/tenants
```

---

## Get Tenant

```http
GET /platform/tenants/{tenant_id}
```

---

## Update Tenant

```http
PATCH /platform/tenants/{tenant_id}
```

---

## Suspend Tenant

```http
POST /platform/tenants/{tenant_id}/suspend
```

---

## Activate Tenant

```http
POST /platform/tenants/{tenant_id}/activate
```

---

# 5. User Management API

Base:

```http
/users
```

---

## Create User

```http
POST /users
```

### Request

```json
{
  "username": "john",
  "email": "john@example.com",
  "role": "librarian"
}
```

---

## List Users

```http
GET /users
```

### Query Parameters

```http
?page=1
&page_size=20
&role=librarian
```

---

## Get User

```http
GET /users/{user_id}
```

---

## Update User

```http
PATCH /users/{user_id}
```

---

## Disable User

```http
POST /users/{user_id}/disable
```

---

# 6. Books API

Base:

```http
/books
```

---

## Create Book

```http
POST /books
```

### Request

```json
{
  "isbn": "9781234567890",
  "title": "FastAPI Fundamentals",
  "author": "John Doe",
  "publisher": "ABC Publishing",
  "publication_year": 2026,
  "category": "Technology",
  "total_copies": 10
}
```

---

## List Books

```http
GET /books
```

### Query Parameters

```http
?page=1
&page_size=20
&search=fastapi
&author=john
&isbn=9781234567890
```

---

## Get Book

```http
GET /books/{book_id}
```

---

## Update Book

```http
PATCH /books/{book_id}
```

---

## Delete Book

```http
DELETE /books/{book_id}
```

---

# 7. Book Copies API

Base:

```http
/book-copies
```

---

## Create Copy

```http
POST /book-copies
```

### Request

```json
{
  "book_id": "uuid",
  "barcode": "BC-1001",
  "location": "Shelf A"
}
```

---

## List Copies

```http
GET /book-copies
```

---

# 8. Borrowers API

Base:

```http
/borrowers
```

---

## Register Borrower

```http
POST /borrowers
```

### Request

```json
{
  "first_name": "Ahmed",
  "last_name": "Ali",
  "email": "ahmed@example.com",
  "student_id": "ST12345"
}
```

---

## List Borrowers

```http
GET /borrowers
```

---

## Borrower Details

```http
GET /borrowers/{borrower_id}
```

---

## Update Borrower

```http
PATCH /borrowers/{borrower_id}
```

---

## Suspend Borrower

```http
POST /borrowers/{borrower_id}/suspend
```

---

# 9. Loans API

Base:

```http
/loans
```

---

## Issue Book

```http
POST /loans
```

### Request

```json
{
  "borrower_id": "uuid",
  "book_copy_id": "uuid",
  "due_date": "2026-08-01"
}
```

---

## List Loans

```http
GET /loans
```

### Query Parameters

```http
?status=issued
?status=overdue
```

---

## Return Book

```http
POST /loans/{loan_id}/return
```

---

## Mark Lost

```http
POST /loans/{loan_id}/lost
```

---

# 10. Fines API

Base:

```http
/fines
```

---

## List Fines

```http
GET /fines
```

---

## Fine Details

```http
GET /fines/{fine_id}
```

---

## Record Payment

```http
POST /fines/{fine_id}/pay
```

### Request

```json
{
  "amount": 500
}
```

---

## Waive Fine

```http
POST /fines/{fine_id}/waive
```

---

# 11. OCR API

Base:

```http
/ocr
```

---

## Scan Student ID

```http
POST /ocr/student-id
```

### Multipart Form

```http
file=image.jpg
```

### Response

```json
{
  "name": "John Doe",
  "student_id": "ST12345"
}
```

---

## Scan ISBN

```http
POST /ocr/isbn
```

---

## Scan Book Cover

```http
POST /ocr/book-cover
```

---

# 12. Marketplace API

Base:

```http
/bookstore
```

---

## Browse Ebooks

```http
GET /bookstore/ebooks
```

---

## Ebook Details

```http
GET /bookstore/ebooks/{ebook_id}
```

---

## Purchase Ebook

```http
POST /bookstore/ebooks/{ebook_id}/purchase
```

---

## My Purchases

```http
GET /bookstore/my-library
```

---

# 13. Reader API

Base:

```http
/reader
```

---

## Save Reading Progress

```http
POST /reader/progress
```

### Request

```json
{
  "ebook_id": "uuid",
  "progress_percent": 40,
  "last_page": 120
}
```

---

## Get Reading Progress

```http
GET /reader/progress/{ebook_id}
```

---

## Create Bookmark

```http
POST /reader/bookmarks
```

### Request

```json
{
  "ebook_id": "uuid",
  "page": 55,
  "note": "Important section"
}
```

---

## List Bookmarks

```http
GET /reader/bookmarks
```

---

## Add Favorite

```http
POST /reader/favorites
```

---

# 14. Reviews API

Base:

```http
/reviews
```

---

## Create Review

```http
POST /reviews
```

### Request

```json
{
  "ebook_id": "uuid",
  "rating": 5,
  "comment": "Excellent book."
}
```

---

## List Reviews

```http
GET /reviews
```

---

# 15. Payments API

Base:

```http
/payments
```

---

## Create Checkout Session

```http
POST /payments/checkout
```

### Request

```json
{
  "type": "ebook_purchase",
  "resource_id": "uuid"
}
```

---

## Payment Webhook

```http
POST /payments/webhooks/stripe
```

```http
POST /payments/webhooks/paystack
```

---

## Payment History

```http
GET /payments
```

---

# 16. Notifications API

Base:

```http
/notifications
```

---

## List Notifications

```http
GET /notifications
```

---

## Mark As Read

```http
POST /notifications/{notification_id}/read
```

---

# 17. Analytics API

Base:

```http
/analytics
```

---

## Dashboard Summary

```http
GET /analytics/dashboard
```

### Response

```json
{
  "active_borrowers": 120,
  "books_issued": 450,
  "overdue_books": 17,
  "fines_collected": 15000
}
```

---

## Borrowing Trends

```http
GET /analytics/borrowing-trends
```

---

## Revenue Analytics

```http
GET /analytics/revenue
```

---

# 18. Audit Logs API

Base:

```http
/audit-logs
```

---

## List Audit Logs

```http
GET /audit-logs
```

### Query Parameters

```http
?page=1
&page_size=20
&resource_type=book
```

---

# 19. Health & Monitoring API

Base:

```http
/system
```

---

## Health Check

```http
GET /system/health
```

Response:

```json
{
  "status": "healthy"
}
```

---

## Readiness Check

```http
GET /system/readiness
```

---

## Liveness Check

```http
GET /system/liveness
```

---

# 20. API Versioning Strategy

Current Version:

```http
/api/v1
```

Future Versions:

```http
/api/v2
/api/v3
```

Rules:

* Breaking changes require a new version.
* Backward-compatible changes remain within the same version.
* Deprecated endpoints must be supported for at least one major release cycle.

```
```
