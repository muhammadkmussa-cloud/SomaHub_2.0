# SomaHub Enterprise Product Requirements Document (PRD)

## Version

2.0

---

# Executive Summary

SomaHub is a multi-tenant Library Management and Digital Reading Platform designed for schools, colleges, universities, and educational institutions.

The platform combines:

* Physical library inventory management
* Borrowing and returns management
* OCR-assisted cataloging
* Digital bookstore
* Secure in-platform ebook reading
* Analytics and reporting
* Automated notifications
* Subscription management

The platform is built using a modern FastAPI architecture with PostgreSQL, Redis, Docker, and Google Cloud Run.

---

# Product Vision

Build the modern operating system for libraries by simplifying library operations while encouraging a stronger reading culture through digital access to books.

---

# Business Goals

* Support 1,000+ libraries
* Support thousands of concurrent readers
* Automate cataloging and borrowing workflows
* Enable digital book sales
* Reduce operational costs for institutions
* Improve reading engagement through digital access

---

# User Roles

## Super Admin

System-wide administration.

Capabilities:

* Manage tenants
* Manage digital bookstore
* Configure subscription plans
* View platform analytics
* View revenue analytics
* Manage global settings
* Manage uploaded ebooks
* Manage marketplace pricing

Maximum allowed:

* 5 Super Admins

---

## Library Administrator

Capabilities:

* Create librarian accounts
* Manage library settings
* Configure fine policies
* View analytics
* Manage subscriptions
* Access all library data

---

## Librarian

Capabilities:

* Catalog books
* Scan books using OCR
* Register borrowers
* Issue books
* Process returns
* Collect fines
* Send reminders
* Manage inventory

---

## Public Reader

Capabilities:

* Browse digital bookstore
* Purchase ebooks
* Read books inside platform
* Track reading progress
* Leave reviews and ratings
* Save favorites
* Receive recommendations

---

# Core Features

## Library Management

### Catalog Management

Features:

* Add books manually
* OCR-assisted cataloging
* ISBN scanning
* Book cover scanning
* Copy tracking
* Availability tracking

### Borrower Management

Features:

* Register borrowers
* Student ID scanning
* Borrower history
* Membership tracking

### Circulation

Features:

* Issue books
* Return books
* Due dates
* Fine calculation
* Fine collection

---

## Digital Bookstore

Features:

* Browse ebooks
* Search by title
* Search by author
* Search by category
* Purchase ebooks
* Reader library
* Ratings and reviews
* Wishlist / favorites

---

## Reader Experience

Features:

* In-platform reader
* Reading progress
* Continue reading
* Fullscreen mode
* Bookmarks
* Reading statistics

---

## OCR Module

Supported scans:

### Student ID

Extract:

* Name
* Student ID
* Admission Number

### ISBN Barcode

Extract:

* ISBN
* Title
* Author

### Book Cover

Extract:

* Title
* Author
* Metadata

Workflow:

Upload
→ OCR Processing
→ Validation
→ Review
→ Save

---

## Notifications

Channels:

* Email
* SMS (future)
* Push Notifications (future)

Types:

* Overdue reminders
* Fine notifications
* Password resets
* Purchase confirmations
* Subscription reminders

---

## Analytics

Library Analytics:

* Active borrowers
* Books issued
* Overdue books
* Fines collected
* Inventory statistics

Platform Analytics:

* Total tenants
* Revenue
* Marketplace sales
* Reader growth

---

# Multi-Tenant Architecture

Model:

Shared database with strict tenant isolation.

Security:

* PostgreSQL Row Level Security (RLS)
* Tenant-scoped queries
* Role-based permissions

Required field:

tenant_id UUID

Every tenant-owned table must include tenant_id.

---

# Technology Stack

## Frontend

* React 19
* TypeScript
* Tailwind CSS
* TanStack Query
* React Router

---

## Backend

* FastAPI
* Uvicorn
* SQLAlchemy 2.0
* Alembic
* PostgreSQL
* Redis
* Pydantic Settings

---

## Authentication & Security

* JWT Access Tokens
* Refresh Tokens
* Argon2 Password Hashing
* Role-Based Access Control (RBAC)
* PostgreSQL RLS
* Audit Logging

Libraries:

* PyJWT
* pwdlib[argon2]

---

## OCR & AI

* Gemini API
* Pillow

Capabilities:

* OCR extraction
* Metadata extraction
* Document processing

---

## Storage

* Supabase Storage

Stores:

* Ebook PDFs
* Book Covers
* OCR Uploads
* User Avatars

---

## Notifications

* Resend
* aiosmtplib

---

## Testing

* Pytest
* HTTPX
* pytest-asyncio
* unittest.mock

---

## Containerization

* Docker
* Docker Compose

Containers:

* Frontend
* Backend
* PostgreSQL
* Redis

---

## Cloud Infrastructure

### Google Cloud Platform

Services:

* Cloud Run
* Cloud Build
* Artifact Registry

Benefits:

* Serverless containers
* Auto scaling
* Managed deployments
* Reduced infrastructure maintenance

---

## Database Hosting

* Neon PostgreSQL

---

# Security Architecture

Application Security:

* Argon2 Password Hashing
* JWT Authentication
* Input Validation
* Secure Cookies
* Rate Limiting
* Audit Logging

Infrastructure Security:

* HTTPS
* Cloud Run Security Controls

For VPS deployments:

* UFW Firewall
* Fail2Ban Protection
* Nginx Reverse Proxy

---

# Deployment Pipeline

GitHub
↓
GitHub Actions
↓
Cloud Build
↓
Artifact Registry
↓
Cloud Run

---

# Monitoring

Tools:

* OpenTelemetry
* Cloud Monitoring
* Cloud Logging

Metrics:

* Response Time
* Error Rate
* Queue Depth
* Revenue Metrics
* Active Users

---

# Acceptance Criteria

The platform must:

* Support multi-tenancy
* Enforce PostgreSQL RLS
* Support Stripe and Paystack
* Support OCR ingestion
* Support bookstore purchases
* Support secure ebook reading
* Support notifications
* Support analytics
* Support Cloud Run deployment
* Support Docker containerization

---

# Future Roadmap

Phase 2:

* Mobile Apps
* Offline Reading
* AI Recommendations
* Reading Streaks
* Institution Federation
* SMS Notifications
* Push Notifications
* Advanced Analytics
* Multi-language Support
