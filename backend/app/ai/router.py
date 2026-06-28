"""
AI API router — chat, document ingestion, OCR, and knowledge management endpoints.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.ai.app_knowledge import AppKnowledgeBase
from app.ai.book_indexer import BookIndexer
from app.ai.config import ai_settings
from app.ai.embeddings import EmbeddingService
from app.ai.ingestion import IngestionPipeline
from app.ai.ocr import OCRPipeline
from app.ai.ollama_client import OllamaClient
from app.ai.rag import RAGPipeline
from app.ai.vectorstore import get_vector_store
from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.books.schemas import BookCreate
from app.modules.books.service import BookService

logger = logging.getLogger("somahub.ai.router")

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    answer: str
    citations: list[dict] = []
    sources: list[dict] = []
    context_used: bool = False


class IngestionResponse(BaseModel):
    chunks_indexed: int
    filename: str


class IndexStatusResponse(BaseModel):
    vector_store_count: int
    ollama_status: str
    ollama_models: list[str]


class OCRResponse(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    authors: list[str] = []
    publisher: str | None = None
    isbn: str | None = None
    publication_year: int | None = None
    edition: str | None = None
    language: str | None = None
    categories: list[str] = []
    description: str | None = None
    subjects: list[str] = []


def get_ollama() -> OllamaClient:
    return OllamaClient()


def get_rag() -> RAGPipeline:
    return RAGPipeline()


def get_ingestion() -> IngestionPipeline:
    return IngestionPipeline()


def get_ocr() -> OCRPipeline:
    return OCRPipeline()


def get_app_knowledge() -> AppKnowledgeBase:
    return AppKnowledgeBase()


def get_book_indexer() -> BookIndexer:
    return BookIndexer()


# ── Chat ────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def chat(
    request: ChatRequest,
    rag: RAGPipeline = Depends(get_rag),
):
    """Chat with the AI assistant using RAG. Supports streaming."""
    if request.stream:
        stream = await rag.query(
            question=request.message,
            history=request.history,
            stream=True,
        )

        async def generate():
            async for chunk in stream:
                if isinstance(chunk, str):
                    yield chunk

        return StreamingResponse(
            generate(),
            media_type="application/x-ndjson",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    result = await rag.query(
        question=request.message,
        history=request.history,
        stream=False,
    )
    return ChatResponse(
        answer=result.get("answer", ""),
        citations=result.get("citations", []),
        sources=result.get("sources", []),
        context_used=result.get("context_used", False),
    )


# ── Document ingestion ──────────────────────────────────────────────────────

@router.post(
    "/ingest",
    response_model=IngestionResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def ingest_document(
    file: UploadFile = File(...),
    ingestion: IngestionPipeline = Depends(get_ingestion),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    content = await file.read()
    max_bytes = ai_settings.INGESTION_MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds max size of {ai_settings.INGESTION_MAX_FILE_SIZE_MB}MB",
        )
    try:
        chunks = await ingestion.ingest(content, file.filename)
        return IngestionResponse(chunks_indexed=chunks, filename=file.filename)
    except Exception as e:
        logger.error("Ingestion failed for %s: %s", file.filename, e)
        raise HTTPException(status_code=500, detail=f"Failed to ingest: {e}")


@router.post(
    "/ingest/text",
    response_model=IngestionResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def ingest_text(
    text: str = Form(...),
    source_id: str = Form(...),
    source_type: str = Form("text"),
    ingestion: IngestionPipeline = Depends(get_ingestion),
):
    try:
        chunks = await ingestion.ingest_text(text=text, source_id=source_id, source_type=source_type)
        return IngestionResponse(chunks_indexed=chunks, filename=source_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest text: {e}")


# ── OCR ─────────────────────────────────────────────────────────────────────

@router.post(
    "/ocr",
    response_model=OCRResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def ocr_image(
    file: UploadFile = File(...),
    ocr: OCRPipeline = Depends(get_ocr),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    try:
        metadata = await ocr.process_book_image(content)
        return OCRResponse(**metadata)
    except Exception as e:
        logger.error("OCR failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")


@router.post(
    "/ocr/catalog",
    response_model=dict,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARIAN))],
)
async def ocr_catalog(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    ocr: OCRPipeline = Depends(get_ocr),
    db: DBSession = None,
    book_indexer: BookIndexer = Depends(get_book_indexer),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    try:
        metadata = await ocr.process_book_image(content)
        title = metadata.get("title") or "Unknown Title"
        authors = metadata.get("authors", [])
        author_str = ", ".join(authors) if authors else "Unknown Author"
        book_data = BookCreate(
            title=title,
            author=author_str,
            publisher=metadata.get("publisher"),
            isbn=metadata.get("isbn"),
            publication_year=metadata.get("publication_year"),
            category=metadata.get("categories", [None])[0] if metadata.get("categories") else None,
            description=metadata.get("description"),
            total_copies=1,
        )
        tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
        service = BookService(db)
        book = await service.create_book(tenant_id, book_data)
        await db.commit()
        await book_indexer.index_book(book)
        return {"book_id": str(book.id), "metadata": OCRResponse(**metadata).model_dump()}
    except Exception as e:
        await db.rollback()
        logger.error("OCR cataloging failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OCR cataloging failed: {e}")


# ── Knowledge base management ───────────────────────────────────────────────

@router.post(
    "/knowledge/index-app",
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def index_app_knowledge(
    app_knowledge: AppKnowledgeBase = Depends(get_app_knowledge),
):
    try:
        total = await app_knowledge.index_all()
        return {"status": "ok", "entries_indexed": total}
    except Exception as e:
        logger.error("App knowledge indexing failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")


@router.post(
    "/knowledge/index-books",
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def index_all_books(
    book_indexer: BookIndexer = Depends(get_book_indexer),
    db: DBSession = None,
):
    try:
        tenant_id = None
        total = await book_indexer.index_books_batch(db, tenant_id)
        return {"status": "ok", "books_indexed": total}
    except Exception as e:
        logger.error("Book indexing failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Book indexing failed: {e}")


# ── Status ──────────────────────────────────────────────────────────────────

@router.get("/status")
async def ai_status(ollama: OllamaClient = Depends(get_ollama)):
    ollama_status = await ollama.health()
    vs = get_vector_store()
    vector_count = await vs.count()
    return IndexStatusResponse(
        vector_store_count=vector_count,
        ollama_status=ollama_status.get("status", "unknown"),
        ollama_models=ollama_status.get("models", []),
    )


@router.get(
    "/models",
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def list_models(
    ollama: OllamaClient = Depends(get_ollama),
):
    models = await ollama.list_models()
    return {"models": models, "configured": {
        "chat": ai_settings.CHAT_MODEL,
        "embedding": ai_settings.EMBEDDING_MODEL,
        "vision": ai_settings.VISION_MODEL,
    }}


# ── Search ──────────────────────────────────────────────────────────────────

@router.post("/search")
async def search_knowledge(
    query: str = Query(..., min_length=1),
    top_k: int = Query(default=5, le=20),
    filter_category: str | None = Query(default=None),
):
    vs = get_vector_store()
    embeddings = EmbeddingService()
    query_embedding = await embeddings.embed_query(query)
    filters = {"category": filter_category} if filter_category else None
    results = await vs.similarity_search(
        query_embedding=query_embedding,
        top_k=top_k,
        filter=filters,
    )
    return {
        "results": [
            {
                "text": r["text"],
                "source": r["metadata"].get("source", "Unknown"),
                "category": r["metadata"].get("category", "general"),
                "score": r["score"],
            }
            for r in results
        ],
        "total": len(results),
    }
