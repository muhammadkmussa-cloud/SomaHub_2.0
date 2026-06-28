# SomaHub AI Assistant — RAG, OCR & Chatbot System

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                   User Interface                          │
│  ┌──────────────┐  ┌──────────────────────────────────┐  │
│  │ Public Pages  │  │     Floating Chatbot (React)     │  │
│  │ (Landing,     │  │  ┌─────────────────────────────┐ │  │
│  │  Auth, etc.)  │  │  │ ChatbotPanel                │ │  │
│  └──────────────┘  │  │  ┌─────────┐ ┌───────────┐  │ │  │
│                    │  │  │Messages │ │  Input    │  │ │  │
│                    │  │  └─────────┘ └───────────┘  │ │  │
│                    │  └─────────────────────────────┘ │  │
│                    └──────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │ API (/api/v1/ai/*)
                       ▼
┌──────────────────────────────────────────────────────────┐
│                FastAPI Backend                            │
│                                                          │
│  ┌─────────────────┐    ┌───────────────────────────┐    │
│  │   AI Router     │───▶│   RAG Pipeline             │    │
│  │  - /chat        │    │   - embed question         │    │
│  │  - /ingest      │    │   - search vector store    │    │
│  │  - /ocr         │    │   - build context          │    │
│  │  - /ocr/catalog │    │   - generate answer        │    │
│  │  - /search      │    │   - stream response        │    │
│  │  - /status      │    └───────────┬───────────────┘    │
│  └─────────────────┘                │                    │
│            │                        │                    │
│            ▼                        ▼                    │
│  ┌─────────────────┐    ┌───────────────────────────┐    │
│  │ IngestionPipeline│   │    Vector Store            │    │
│  │ - text extract   │   │    (ChromaDB)              │    │
│  │ - chunk          │──▶│    - add_texts             │    │
│  │ - embed          │   │    - similarity_search     │    │
│  │ - store          │   │    - delete                │    │
│  └─────────────────┘    └───────────────────────────┘    │
│            │                    ▲                        │
│            ▼                    │                        │
│  ┌─────────────────┐    ┌───────────────────────────┐    │
│  │  OCR Pipeline   │    │  Embedding Service        │    │
│  │  - book metadata│    │  (Ollama nomic-embed-text) │    │
│  │  - text extract │    └───────────────────────────┘    │
│  │  - auto-catalog │                                      │
│  └─────────────────┘                                      │
│            │                                               │
│            ▼                                               │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Ollama (Local LLM)                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ Chat     │  │ Vision   │  │ Embeddings       │  │  │
│  │  │ qwen3    │  │ granite  │  │ nomic-embed-text │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Module Structure

```
backend/app/ai/
├── __init__.py          # Module exports
├── config.py            # AI settings (models, chunking, vector store)
├── ollama_client.py     # Ollama HTTP client (chat, vision, embeddings)
├── embeddings.py        # Embedding service (cached)
├── vectorstore.py       # ChromaDB vector store abstraction
├── text_extractor.py    # Text extraction from PDF, DOCX, TXT, MD, CSV, JSON, EPUB, Images
├── chunker.py           # Semantic text chunking
├── ingestion.py         # Ingestion pipeline (extract → chunk → embed → store)
├── ocr.py               # OCR pipeline using Ollama vision models
├── rag.py               # RAG query pipeline (search → context → generate)
├── app_knowledge.py     # App navigation, workflows, FAQs knowledge base
├── book_indexer.py      # Book metadata indexing
├── prompts.py           # Prompt templates
├── router.py            # FastAPI router (chat, ingest, OCR, status)
└── AI_README.md         # This documentation
```

## Installation

### 1. Install Ollama

```bash
# Linux / macOS
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

### 2. Pull Required Models

```bash
# Chat model (default: qwen3:8b — ~4.7GB)
ollama pull qwen3:8b

# Alternative chat models:
ollama pull llama3.1:8b      # Meta Llama 3.1
ollama pull mistral:7b       # Mistral 7B
ollama pull gemma3:7b        # Google Gemma 3

# Embedding model (small, fast)
ollama pull nomic-embed-text

# Alternative embedding models:
ollama pull mxbai-embed-large
ollama pull bge-m3

# Vision model for OCR (default)
ollama pull granite-vision:latest

# Alternative vision models:
ollama pull llama3.2-vision:11b
ollama pull qwen2.5-vl:7b
ollama pull llava:13b
ollama pull minicpm-v:8b
```

### 3. Install Python Dependencies

```bash
cd backend
uv sync
# The following packages are added:
# - chromadb: Vector database
# - pypdf2 / pypdf: PDF text extraction
# - python-docx: DOCX text extraction
```

### 4. Environment Variables

Create or update `backend/.env`:

```env
# Required - Ollama host
OLLAMA_HOST=http://localhost:11434

# Optional - Model overrides
AI_CHAT_MODEL=qwen3:8b
AI_EMBEDDING_MODEL=nomic-embed-text
AI_VISION_MODEL=granite-vision:latest

# Optional - Chunking
AI_CHUNK_SIZE=512
AI_CHUNK_OVERLAP=64

# Optional - Retrieval
AI_RETRIEVAL_TOP_K=5

# Optional - Vector store
AI_VECTOR_STORE_PATH=data/vectordb
AI_VECTOR_STORE_COLLECTION=somahub_knowledge

# Optional - OCR
AI_OCR_ENABLED=true
```

### 5. Run the Application

```bash
# Start the backend
cd backend
uv run uvicorn app.main:app --reload

# Start the frontend (separate terminal)
cd frontend
npm run dev
```

## API Endpoints

All endpoints are under `/api/v1/ai`.

### Chat

**`POST /api/v1/ai/chat`** — Chat with the AI assistant (RAG-powered)

```json
// Request
{
  "message": "How do I borrow a book?",
  "history": [{"role": "user", "content": "..."}],
  "stream": true
}

// Response (streaming, ndjson format):
// {"type":"citations","data":[{"source":"...","type":"workflow","text_snippet":"...","score":0.92}]}
// {"type":"token","data":"To borrow a book..."}
// {"type":"done","data":true}

// Response (non-streaming):
{
  "answer": "To borrow a book, go to /dashboard/loans...",
  "citations": [...],
  "sources": [...],
  "context_used": true
}
```

### Document Ingestion

**`POST /api/v1/ai/ingest`** — Upload and index a document

```
Form data: file=<upload>
```

Response:
```json
{"chunks_indexed": 12, "filename": "document.pdf"}
```

**`POST /api/v1/ai/ingest/text`** — Ingest raw text

```
Form data: text=...&source_id=memo-1&source_type=text
```

### OCR

**`POST /api/v1/ai/ocr`** — Extract book metadata from image

```
Form data: file=<image>
```

Response:
```json
{
  "title": "Atomic Habits",
  "authors": ["James Clear"],
  "publisher": "Penguin",
  "isbn": "9780735211292",
  "publication_year": 2018,
  "categories": ["Self-Help"],
  "description": "...",
  ...
}
```

**`POST /api/v1/ai/ocr/catalog`** — OCR + auto-create book record

Response:
```json
{
  "book_id": "uuid-of-created-book",
  "metadata": { ... }
}
```

### Knowledge Base Management

**`POST /api/v1/ai/knowledge/index-app`** — Index app navigation & FAQs

**`POST /api/v1/ai/knowledge/index-books`** — Re-index all books

### Search & Status

**`POST /api/v1/ai/search?query=...&top_k=5&filter_category=book`** — Search indexed knowledge

**`GET /api/v1/ai/status`** — AI subsystem health

**`GET /api/v1/ai/models`** — List available Ollama models

## Indexing Process

### Automatic Indexing Triggers

1. **App navigation**: Indexed automatically on server startup (if `AI_APP_KNOWLEDGE_ENABLED=true`)
2. **Books**: Automatically indexed when created, updated, or deleted via the BookService
3. **Document uploads**: Indexed on demand via `POST /api/v1/ai/ingest`
4. **OCR cataloging**: Books created via OCR are automatically indexed

### File Types Supported

| Type | Extension | Library Required |
|------|-----------|-----------------|
| PDF | .pdf | PyPDF2 / pypdf |
| Word | .docx | python-docx |
| Text | .txt | None |
| Markdown | .md | None |
| CSV | .csv | None |
| JSON | .json | None |
| EPUB | .epub | EbookLib + BeautifulSoup4 |
| Images | .png, .jpg, .jpeg, .gif, .bmp, .webp, .tiff | Pillow + Ollama vision |

### Pipeline Steps

```
Upload → Detect type → Extract text → Split into chunks → Generate embeddings → Store in ChromaDB
```

## OCR Workflow

```
Upload image → Detect image type → Base64 encode → Send to Ollama vision model
→ Parse JSON metadata → (Optional) Auto-create book record in database
→ Index book in vector store
```

## Chatbot Workflow

```
User question → Generate embedding → Search ChromaDB → Retrieve top K chunks
→ Build context from chunks → Send context + question to Ollama chat model
→ Stream response back to UI → Display with citations
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `AI_CHAT_MODEL` | `qwen3:8b` | Chat model name |
| `AI_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `AI_VISION_MODEL` | `granite-vision:latest` | Vision model for OCR |
| `AI_CHUNK_SIZE` | `512` | Characters per chunk |
| `AI_CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `AI_RETRIEVAL_TOP_K` | `5` | Number of chunks to retrieve |
| `AI_CHAT_TEMPERATURE` | `0.7` | LLM temperature (0.0-1.0) |
| `AI_CHAT_MAX_TOKENS` | `2048` | Max output tokens |
| `AI_VECTOR_STORE_TYPE` | `chromadb` | Vector database type |
| `AI_VECTOR_STORE_PATH` | `data/vectordb` | ChromaDB persistence path |
| `AI_VECTOR_STORE_COLLECTION` | `somahub_knowledge` | Collection name |
| `AI_OCR_ENABLED` | `true` | Enable OCR |
| `AI_APP_KNOWLEDGE_ENABLED` | `true` | Auto-index app knowledge |

## Adding New Models

Edit `backend/app/ai/config.py`:

```python
# Change chat model
CHAT_MODEL: str = "llama3.1:8b"

# Change embedding model
EMBEDDING_MODEL: str = "mxbai-embed-large"

# Change vision model
VISION_MODEL: str = "llama3.2-vision:11b"
```

Or set environment variables:

```bash
export AI_CHAT_MODEL=llama3.1:8b
export AI_EMBEDDING_MODEL=mxbai-embed-large
export AI_VISION_MODEL=llama3.2-vision:11b
```

## Future Provider Support

The architecture is provider-agnostic. To add OpenAI, Anthropic, or another provider:

1. Create a new client class implementing the same interface as `OllamaClient`
2. Update `config.py` to add provider selection
3. Update the factory in `ollama_client.py` or create a new provider factory

## Troubleshooting

### Ollama connection refused

```bash
# Ensure Ollama is running
ollama serve

# Check if Ollama is listening
curl http://localhost:11434/api/tags
```

### Model not found

```bash
# Pull the required model
ollama pull qwen3:8b
ollama pull nomic-embed-text
ollama pull granite-vision:latest
```

### ChromaDB errors

```bash
# Delete and recreate the vector store
rm -rf backend/data/vectordb
mkdir -p backend/data/vectordb
# The index will be rebuilt on next startup
```

### No results from chatbot

1. Check that app knowledge has been indexed: `POST /api/v1/ai/knowledge/index-app`
2. Verify vector store status: `GET /api/v1/ai/status`
3. Check Ollama is running and has the required models

### Slow responses

- Use a smaller chat model (e.g., `qwen3:4b` instead of `qwen3:8b`)
- Reduce `AI_RETRIEVAL_TOP_K` to 3
- Reduce `CHUNK_SIZE` to 256

## Security Notes

- The chatbot is designed for public users and does not expose admin functionality
- All AI endpoints respect role-based permissions
- Chat queries go through RAG — the LLM does not have direct database access
- Sensitive information (passwords, API keys, server config) is never exposed
- OCR processing happens locally — no data leaves your server

## Deployment

For production deployment:

1. Ensure Ollama is running as a systemd service
2. Set `AI_OLLAMA_HOST` to the Ollama service URL
3. Use a production-grade vector store (consider Qdrant or pgvector for large scale)
4. Set up logging with `AI_AI_LOG_LEVEL=INFO`
5. Ensure the `data/vectordb` directory is on persistent storage
6. Consider running a separate indexing worker for large document batches
