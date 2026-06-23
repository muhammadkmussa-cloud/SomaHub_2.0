# SomaHub Enterprise

# Role-Based Access Control (RBAC) & Permission Matrix

Version: 1.0

---

# 1. Overview

SomaHub uses Role-Based Access Control (RBAC) to enforce authorization across the platform.

Authorization is implemented at:

* API Layer (FastAPI Dependencies)
* Service Layer
* Database Layer (PostgreSQL RLS)

---

# 2. User Hierarchy

## Platform Users

```text
super_admin
```

---

## Tenant Users

```text
library_admin
librarian
reader
```

---

# 3. Permission Naming Convention

Format:

```text
resource:action
```

Examples:

```text
books:create
books:update
books:delete

borrowers:create
borrowers:update

loans:issue
loans:return

analytics:view
```

---

# 4. Platform Permissions

## Super Admin

Full platform access.

Permissions:

```text
platform:manage

tenants:create
tenants:view
tenants:update
tenants:suspend
tenants:activate
tenants:delete

subscriptions:view
subscriptions:update

marketplace:create
marketplace:update
marketplace:delete

platform_analytics:view

audit_logs:view

system_settings:update
```

---

# 5. Tenant Permissions

## Library Admin

Highest tenant-level role.

Permissions:

```text
library:view
library:update

users:create
users:view
users:update
users:deactivate

books:create
books:view
books:update
books:delete

borrowers:create
borrowers:view
borrowers:update
borrowers:suspend

loans:issue
loans:return
loans:view

fines:create
fines:view
fines:waive
fines:collect

notifications:create
notifications:view

analytics:view

ocr:scan

reports:view
reports:export
```

---

## Librarian

Operational role.

Permissions:

```text
books:create
books:view
books:update

borrowers:create
borrowers:view
borrowers:update

loans:issue
loans:return
loans:view

fines:view
fines:collect

notifications:create
notifications:view

ocr:scan

reports:view
```

Restrictions:

```text
Cannot manage users
Cannot delete books
Cannot waive fines
Cannot access subscription settings
Cannot access tenant settings
```

---

## Reader

Digital library user.

Permissions:

```text
profile:view
profile:update

bookstore:view

ebooks:purchase

reader:view

reading_progress:create
reading_progress:update

bookmarks:create
bookmarks:view
bookmarks:delete

favorites:create
favorites:view
favorites:delete

reviews:create
reviews:update
reviews:delete

notifications:view
```

Restrictions:

```text
Cannot access library management
Cannot access analytics
Cannot access borrowers
Cannot access loans
Cannot access fines
Cannot access administration
```

---

# 6. Permission Matrix

| Resource           | Super Admin | Library Admin | Librarian | Reader |
| ------------------ | ----------- | ------------- | --------- | ------ |
| Tenants View       | ✓           | ✗             | ✗         | ✗      |
| Tenants Create     | ✓           | ✗             | ✗         | ✗      |
| Tenants Suspend    | ✓           | ✗             | ✗         | ✗      |
| Users View         | ✗           | ✓             | ✗         | ✗      |
| Users Create       | ✗           | ✓             | ✗         | ✗      |
| Users Update       | ✗           | ✓             | ✗         | ✗      |
| Books View         | ✓           | ✓             | ✓         | ✓      |
| Books Create       | ✗           | ✓             | ✓         | ✗      |
| Books Update       | ✗           | ✓             | ✓         | ✗      |
| Books Delete       | ✗           | ✓             | ✗         | ✗      |
| Borrowers View     | ✗           | ✓             | ✓         | ✗      |
| Borrowers Create   | ✗           | ✓             | ✓         | ✗      |
| Borrowers Suspend  | ✗           | ✓             | ✗         | ✗      |
| Loans View         | ✗           | ✓             | ✓         | ✗      |
| Loans Issue        | ✗           | ✓             | ✓         | ✗      |
| Loans Return       | ✗           | ✓             | ✓         | ✗      |
| Fines View         | ✗           | ✓             | ✓         | ✗      |
| Fines Collect      | ✗           | ✓             | ✓         | ✗      |
| Fines Waive        | ✗           | ✓             | ✗         | ✗      |
| OCR Scan           | ✗           | ✓             | ✓         | ✗      |
| Analytics View     | ✓           | ✓             | ✗         | ✗      |
| Marketplace Manage | ✓           | ✗             | ✗         | ✗      |
| Ebook Purchase     | ✗           | ✗             | ✗         | ✓      |
| Reader Module      | ✗           | ✗             | ✗         | ✓      |
| Notifications View | ✓           | ✓             | ✓         | ✓      |
| Audit Logs View    | ✓           | ✗             | ✗         | ✗      |

---

# 7. FastAPI Authorization Design

JWT Payload:

## Platform User

```json
{
  "sub": "user_id",
  "user_type": "platform",
  "role": "super_admin"
}
```

---

## Tenant User

```json
{
  "sub": "user_id",
  "tenant_id": "tenant_uuid",
  "user_type": "tenant",
  "role": "library_admin"
}
```

---

# 8. Permission Dependency Pattern

Example:

```python
@router.post("/books")
async def create_book(
    current_user=Depends(
        require_permission("books:create")
    )
):
    ...
```

---

# 9. Permission Groups

To reduce duplication, permissions are grouped.

## Books

```text
books:view
books:create
books:update
books:delete
```

---

## Borrowers

```text
borrowers:view
borrowers:create
borrowers:update
borrowers:suspend
```

---

## Loans

```text
loans:view
loans:issue
loans:return
```

---

## Fines

```text
fines:view
fines:collect
fines:waive
```

---

## Users

```text
users:view
users:create
users:update
users:deactivate
```

---

# 10. Ownership Rules

Readers may only access:

```text
their own profile
their own purchases
their own bookmarks
their own reviews
their own reading progress
```

Enforced through:

```text
API checks
Service checks
Database queries
```

---

# 11. Multi-Tenant Enforcement

Every tenant user must be restricted to:

```text
their tenant_id
```

Implemented using:

```text
JWT tenant_id
FastAPI dependencies
PostgreSQL RLS
```

Example:

Tenant A cannot access:

```text
Books
Borrowers
Loans
Fines
Users
Analytics
```

belonging to Tenant B.

---

# 12. Audit Requirements

The following actions must be logged:

```text
Login
Logout
Password Reset

Tenant Creation
Tenant Suspension

Book Creation
Book Update
Book Delete

Borrower Registration

Loan Issuance
Loan Return

Fine Collection

User Creation
User Deactivation
```

---

# 13. Future Roles

Reserved roles for future enterprise expansion:

```text
support_admin
finance_admin
operations_admin

assistant_librarian

institution_manager
```

These roles are not active in Version 1.0 but the RBAC architecture must support them.
