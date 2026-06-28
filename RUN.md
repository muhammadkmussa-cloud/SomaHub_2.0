# SomaHub — Quick Start

## Prerequisites

- PostgreSQL running on localhost:5432 (database `somahub`)
- Ollama running on localhost:11434

## First-Time Setup

### 1. Environment variables

```bash
# Backend — already pre-filled with dev defaults
# Just add your SECRET_KEY for production
cp backend/.env.example backend/.env   # if .env doesn't exist yet

# Frontend
cp frontend/.env.example frontend/.env
```

### 2. Pull Ollama Models

```bash
ollama pull nomic-embed-text    # embeddings (required for RAG)
ollama pull llama3:latest       # chat (fallback — works)
# Optional:
ollama pull qwen3:8b            # preferred chat model
ollama pull granite-vision:latest  # OCR
```

## Run Backend

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- First startup auto-runs Alembic migrations.
- Dev superadmin created automatically: `admin@somahub.io / Admin123!`
- App knowledge (navigation, workflows, FAQs) auto-indexed on startup.
- Embeds via `nomic-embed-text`, chat via `llama3:latest`.

## Run Frontend

```bash
cd frontend
npm install   # first time only
npm run dev
```
Opens at `http://localhost:5173/`.

## Verify

| What | URL / Command |
|------|--------------|
| Backend health | `curl http://localhost:8000/health` |
| AI status | `curl http://localhost:8000/api/v1/ai/status` |
| Chat test | `curl -X POST http://localhost:8000/api/v1/ai/chat -H "Content-Type: application/json" -d '{"message":"Hi","stream":false}'` |
| Login test | `curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"admin@somahub.io","password":"Admin123!"}'` |
| Frontend | Open `http://localhost:5173/` in browser |

## Chatbot

- Floating button appears bottom-right on every page.
- Press `Ctrl+B` to toggle chat panel.
- No login required for chat.

## Useful Commands

```bash
# Re-index app knowledge
curl -X POST http://localhost:8000/api/v1/ai/knowledge/index-app

# Index all books from database
curl -X POST http://localhost:8000/api/v1/ai/knowledge/index-books

# Ingest a document (PDF, DOCX, TXT)
curl -X POST http://localhost:8000/api/v1/ai/ingest -F "file=@/path/to/doc.pdf"

# Seed demo data
cd backend && uv run scripts/seed_dev.py --with-demo

# View backend logs
tail -f /tmp/backend.log
```

## Troubleshooting

### `.venv/bin/uvicorn: cannot execute: required file not found`

The virtual environment was moved from another location. Fix all shebang lines:

```bash
cd backend/.venv/bin
VENV_PYTHON=$(realpath python)
for f in *; do
  if [ -f "$f" ] && [ -x "$f" ] && head -1 "$f" | grep -q "^#!"; then
    sed -i "1s|^#!.*python.*|#!$VENV_PYTHON|" "$f"
  fi
done
```

### `chroma` import fails or `Cannot connect to ChromaDB`

Reinstall the package:

```bash
cd backend && uv sync
```

### Backend fails to start: `relation "users" does not exist`

Run migrations:

```bash
cd backend && uv run alembic upgrade head
```

## Config

Edit `backend/.env` or `backend/app/ai/config.py`:

| Env Var | What it does | Default |
|---------|-------------|---------|
| `AI_CHAT_MODEL` | Chat model name | `llama3:latest` |
| `AI_EMBEDDING_MODEL` | Embedding model name | `nomic-embed-text` |
| `AI_VISION_MODEL` | OCR/vision model name | `granite-vision:latest` |
| `AI_OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `SECRET_KEY` | JWT signing key (set for production) | dev fallback in dev mode |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/somahub` |
| `RESEND_API_KEY` | Email API key | empty (prints to console) |
| `VITE_API_URL` | Frontend API proxy target | `http://localhost:8000/api/v1` |
