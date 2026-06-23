# SomaHub

Multi-tenant library management and digital reading SaaS platform.

## Quick start

```bash
# Start PostgreSQL, Redis, backend, and frontend
docker compose up

# Or run locally
make dev-db          # postgres + redis only
make migrate         # run Alembic migrations
make dev-backend     # FastAPI on :8000
make dev-frontend    # Vite on :5173
```

- **API:** http://localhost:8000/api/v1  
- **API docs (dev):** http://localhost:8000/docs  
- **Frontend:** http://localhost:5173  

## Project structure

```
backend/     FastAPI API (multi-tenant, RBAC, payments)
frontend/    React + Vite dashboard
docs/        Architecture, API, and security guides
```

## Environment

Copy environment files and set secrets:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Tests

```bash
make test              # backend pytest
cd backend && uv run pytest tests/ --cov=app
cd frontend && npm run test
cd frontend && npm run test:e2e
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API overview](docs/API.md)
- [Security checklist](docs/SECURITY.md)
- [Backend setup](backend/README.md)
- [Frontend setup](frontend/README.md)

## License

Proprietary — SomaHub Enterprise.
