SomaHub Enterprise

Modern Library Management & Digital Reading Platform

SomaHub is a multi-tenant library management and digital reading system designed for schools, colleges, universities, and educational institutions. It combines physical inventory management, OCR-assisted cataloging, digital bookstore, secure ebook reading, analytics, and subscription management — all in one platform.
🚀 Features

    Authentication: JWT-based login, refresh tokens, password reset, RBAC.

    Tenant Management: Super Admin controls for libraries, subscriptions, and platform analytics.

    User Management: Roles include Super Admin, Library Admin, Librarian, and Reader.

    Books & Catalog: Manual entry, ISBN scanning, OCR-assisted cataloging, copy tracking.

    Borrowers: Registration, student ID scanning, borrower history, suspension.

    Loans: Issue, return, overdue tracking, fines.

    Digital Bookstore: Browse, purchase, and review ebooks.

    Reader Module: In-platform ebook reader with progress tracking, bookmarks, favorites.

    Payments: Stripe & Paystack integration, checkout sessions, webhooks.

    Notifications: Email, SMS (future), push notifications.

    Analytics: Borrowing trends, revenue, tenant growth, marketplace sales.

    OCR: Student ID, ISBN, and book cover scanning.

🛠️ Tech Stack

    Frontend: React 19, TypeScript, Tailwind CSS, TanStack Query, React Router

    Backend: FastAPI, SQLAlchemy 2.0, Alembic, Redis, Pydantic Settings

    Database: PostgreSQL (Neon), Row Level Security (RLS)

    Storage: Supabase Storage (ebooks, covers, OCR uploads, avatars)

    Infrastructure: Docker, Google Cloud Run, GitHub Actions, Cloud Build, Artifact Registry

    Security: JWT, Argon2, RBAC, RLS, Audit Logging

📂 Project Structure
Code

backend/
  app/
    core/
    modules/
    infrastructure/
    workers/
    tests/
frontend/
  src/
    components/
    pages/
    hooks/
    utils/

⚙️ Installation
bash

# Clone the repository
git clone https://github.com/muhammadkmussa-cloud/SomaHub-1.git
cd SomaHub-1

# Backend setup
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup
cd frontend
npm install
npm run dev

📖 Usage

    Super Admin: Manage tenants, subscriptions, marketplace, analytics.

    Library Admin: Manage librarians, borrowers, books, fines, analytics.

    Librarian: Catalog books, issue/return loans, collect fines.

    Reader: Purchase ebooks, read in-platform, track progress, leave reviews.

📊 Roadmap

    Mobile apps (iOS/Android)

    Offline reading

    AI-powered recommendations

    Institution federation

    Advanced analytics

    Multi-language support

🤝 Contributing

    Fork the repo

    Create a feature branch (git checkout -b feature-name)

    Commit changes (git commit -m "Add feature")

    Push to branch (git push origin feature-name)

    Open a Pull Request

📜 License

MIT License. See LICENSE file for details.
