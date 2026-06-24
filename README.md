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

⚙️ Getting Started (Local Development)

SomaHub uses Docker and Docker Compose to spin up the entire stack (PostgreSQL, Redis, Backend, and Frontend) with hot-reloading for easy development.

### Prerequisites
Make sure you have installed:
- [Docker & Docker Compose](https://docs.docker.com/get-docker/)
- [uv](https://github.com/astral-sh/uv) (Extremely fast Python package manager - used inside the backend)
- [Node.js](https://nodejs.org/) (v20+ recommended)

### 1. Environment Setup
Create the required environment files for the frontend and backend.

```bash
# In the backend directory
cd backend
cp .env.example .env

# In the frontend directory
cd ../frontend
cp .env.example .env
```
*(Note: You do not need to change the values in `.env` for basic local development, as they are pre-configured to work with the Docker setup).*

### 2. Running the Application via Docker (Recommended)
From the root of the repository, simply run:

```bash
docker-compose up --build
```
This will automatically download all dependencies and start the services:
- **Frontend:** Available at `http://localhost:5173`
- **Backend API:** Available at `http://localhost:8000`
- **PostgreSQL:** Running on port `5432`
- **Redis:** Running on port `6379`

### 3. Alternative: Running Manually (Without Docker)

If you prefer to run the apps directly on your host machine without Docker:

**Backend Setup:**
```bash
cd backend
# uv will automatically create a virtual environment and sync dependencies based on uv.lock
uv sync
# Run database migrations
uv run alembic upgrade head
# Start the FastAPI server
uv run uvicorn app.main:app --reload
```

**Frontend Setup:**
```bash
cd frontend
# Install Node modules
npm install
# Start the Vite development server
npm run dev
```

## 🚀 Production Deployment
To run this application in a production environment (optimized builds, no hot-reloading, secure secrets), refer to the `.env.prod.example` and run:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```


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
