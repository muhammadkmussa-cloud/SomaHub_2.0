.PHONY: dev dev-frontend dev-backend migrate migrate-down seed test lint format help prod-up prod-down prod-build

# ── Development ────────────────────────────────────────────────────────────────
dev: ## Start all services with Docker Compose (Local Dev)
	docker compose up --build

dev-d: ## Start all services in detached mode
	docker compose up -d --build

dev-frontend: ## Start Vite frontend dev server (local)
	cd frontend && npm run dev

dev-backend: ## Start FastAPI backend (local)
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-db: ## Start only PostgreSQL and Redis
	docker compose up postgres redis -d

# ── Production ─────────────────────────────────────────────────────────────────
prod-up: ## Start all production services with Docker Compose
	docker compose -f docker-compose.prod.yml up -d

prod-build: ## Build production Docker images
	docker compose -f docker-compose.prod.yml build

prod-down: ## Stop all production containers
	docker compose -f docker-compose.prod.yml down

# ── Database Migrations ────────────────────────────────────────────────────────
migrate: ## Run Alembic migrations (upgrade to head)
	cd backend && uv run alembic upgrade head

migrate-down: ## Rollback last Alembic migration
	cd backend && uv run alembic downgrade -1

migrate-create: ## Create a new Alembic migration (usage: make migrate-create MSG="add users table")
	cd backend && uv run alembic revision --autogenerate -m "$(MSG)"

# ── Testing ────────────────────────────────────────────────────────────────────
test: ## Run all backend tests
	cd backend && uv run pytest tests/ -v

test-cov: ## Run backend tests with coverage
	cd backend && uv run pytest tests/ --cov=app --cov-report=term-missing

test-frontend: ## Run frontend tests
	cd frontend && npm run test

# ── Linting & Formatting ───────────────────────────────────────────────────────
lint: ## Run linters (Frontend + Backend)
	cd backend && uv run ruff check .
	cd frontend && npm run lint

format: ## Auto-format code (Backend)
	cd backend && uv run ruff format .

# ── Docker ─────────────────────────────────────────────────────────────────────
down: ## Stop all dev containers
	docker compose down

down-v: ## Stop all containers and remove volumes (DESTRUCTIVE)
	docker compose down -v
	docker compose -f docker-compose.prod.yml down -v

logs: ## View all container logs
	docker compose logs -f

# ── Database utilities ─────────────────────────────────────────────────────────
db-shell: ## Open psql shell in the postgres container
	docker compose exec postgres psql -U postgres -d somahub

# ── Clean ──────────────────────────────────────────────────────────────────────
clean: ## Remove Python cache files and build artifacts
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/dist

# ── Help ───────────────────────────────────────────────────────────────────────
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
