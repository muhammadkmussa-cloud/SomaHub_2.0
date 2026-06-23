.PHONY: dev dev-frontend dev-backend migrate migrate-down seed test lint format help

# ── Development ────────────────────────────────────────────────────────────────
dev: ## Start all services with Docker Compose
	docker compose up

dev-d: ## Start all services in detached mode
	docker compose up -d

dev-frontend: ## Start Vite frontend dev server (local)
	cd frontend && npm run dev

dev-backend: ## Start FastAPI backend (local)
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
	elif [ -x .venv/bin/uvicorn ]; then \
		.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
	else \
		python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
	fi

dev-db: ## Start only PostgreSQL and Redis (for local dev without Docker frontend/backend)
	docker compose up postgres redis -d

# ── Database Migrations ────────────────────────────────────────────────────────
migrate: ## Run Alembic migrations (upgrade to head)
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run alembic upgrade head; \
	elif [ -x .venv/bin/alembic ]; then \
		.venv/bin/alembic upgrade head; \
	else \
		python3 -m alembic upgrade head; \
	fi

migrate-down: ## Rollback last Alembic migration
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run alembic downgrade -1; \
	elif [ -x .venv/bin/alembic ]; then \
		.venv/bin/alembic downgrade -1; \
	else \
		python3 -m alembic downgrade -1; \
	fi

migrate-create: ## Create a new Alembic migration (usage: make migrate-create MSG="add users table")
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run alembic revision --autogenerate -m "$(MSG)"; \
	elif [ -x .venv/bin/alembic ]; then \
		.venv/bin/alembic revision --autogenerate -m "$(MSG)"; \
	else \
		python3 -m alembic revision --autogenerate -m "$(MSG)"; \
	fi

migrate-history: ## Show migration history
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run alembic history --verbose; \
	elif [ -x .venv/bin/alembic ]; then \
		.venv/bin/alembic history --verbose; \
	else \
		python3 -m alembic history --verbose; \
	fi

# ── Install ────────────────────────────────────────────────────────────────────
	install: ## Install all dependencies
	cd backend && \
	if [ -d .venv ]; then \
		.venv/bin/python -m pip install -e .[dev]; \
	else \
		python3 -m pip install -e backend[dev]; \
	fi
	cd frontend && npm install

# ── Testing ────────────────────────────────────────────────────────────────────
	test: ## Run all tests
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run pytest tests/ -v; \
	elif [ -x .venv/bin/pytest ]; then \
		.venv/bin/pytest tests/ -v; \
	else \
		python3 -m pytest tests/ -v; \
	fi

	test-cov: ## Run tests with coverage
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run pytest tests/ --cov=app --cov-report=term-missing; \
	elif [ -x .venv/bin/pytest ]; then \
		.venv/bin/pytest tests/ --cov=app --cov-report=term-missing; \
	else \
		python3 -m pytest tests/ --cov=app --cov-report=term-missing; \
	fi

# ── Linting & Formatting ───────────────────────────────────────────────────────
	lint: ## Run linters
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run ruff check app/; \
	elif [ -x .venv/bin/ruff ]; then \
		.venv/bin/ruff check app/; \
	else \
		echo "ruff not found in .venv; install dev deps to run linters"; \
	fi
	cd frontend && npm run lint

	format: ## Auto-format code
	cd backend && \
	if [ -x .venv/bin/uv ]; then \
		.venv/bin/uv run ruff format app/; \
	elif [ -x .venv/bin/ruff ]; then \
		.venv/bin/ruff format app/; \
	else \
		echo "ruff not found in .venv; install dev deps to run formatter"; \
	fi
	cd frontend && npm run format

# ── Docker ─────────────────────────────────────────────────────────────────────
build: ## Build Docker images
	docker compose build

down: ## Stop all containers
	docker compose down

down-v: ## Stop all containers and remove volumes (DESTRUCTIVE)
	docker compose down -v

logs: ## View all container logs
	docker compose logs -f

logs-backend: ## View backend logs only
	docker compose logs -f backend

logs-frontend: ## View frontend logs only
	docker compose logs -f frontend

# ── Database utilities ─────────────────────────────────────────────────────────
db-shell: ## Open psql shell in the postgres container
	docker compose exec postgres psql -U postgres -d somahub

redis-cli: ## Open Redis CLI
	docker compose exec redis redis-cli

# ── Clean ──────────────────────────────────────────────────────────────────────
clean: ## Remove Python cache files
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true

# ── Help ───────────────────────────────────────────────────────────────────────
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
