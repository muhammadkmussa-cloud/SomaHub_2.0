# SomaHub Frontend

React + TypeScript + Vite dashboard for SomaHub.

## Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server |
| `npm run build` | Production build |
| `npm run lint` | ESLint |
| `npm run test` | Vitest unit tests |
| `npm run test:e2e` | Playwright smoke tests |

## Environment

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Role-based routes

- **Reader:** Bookstore, dashboard
- **Librarian / Library admin:** Books, borrowers, loans, fines
- **Library admin:** Analytics, settings
- **Super admin:** Tenants, platform admin
