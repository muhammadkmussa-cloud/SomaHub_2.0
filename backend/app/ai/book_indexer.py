"""
Book indexer — indexes book metadata into the vector store for RAG-based book queries.
"""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ingestion import IngestionPipeline
from app.modules.books.models import Book

logger = logging.getLogger("somahub.ai.book_indexer")


class BookIndexer:
    def __init__(self, ingestion_pipeline: IngestionPipeline | None = None):
        self.ingestion = ingestion_pipeline or IngestionPipeline()

    async def index_book(self, book: Book) -> int:
        text = self._book_to_text(book)
        return await self.ingestion.ingest_text(
            text=text,
            source_id=f"book:{book.id}",
            source_type="book",
            extra_metadata={
                "category": "book",
                "book_id": str(book.id),
                "tenant_id": str(book.tenant_id),
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn or "",
                "category": book.category or "",
                "publisher": book.publisher or "",
            },
        )

    async def index_books_batch(
        self, db: AsyncSession, tenant_id: UUID | None = None
    ) -> int:
        query = select(Book)
        if tenant_id:
            query = query.where(Book.tenant_id == tenant_id)
        result = await db.execute(query)
        books = result.scalars().all()

        total = 0
        for book in books:
            try:
                count = await self.index_book(book)
                total += count
            except Exception as e:
                logger.error("Failed to index book %s: %s", book.id, e)
        logger.info("Indexed %d books total", total)
        return total

    async def reindex_book(self, book: Book) -> int:
        await self.remove_book(book.id)
        return await self.index_book(book)

    async def remove_book(self, book_id: UUID) -> None:
        from app.ai.vectorstore import get_vector_store

        vs = get_vector_store()
        await vs.delete_by_filter({"book_id": str(book_id)})
        logger.info("Removed book %s from vector index", book_id)

    def _book_to_text(self, book: Book) -> str:
        parts = [
            f"Title: {book.title}",
            f"Author: {book.author}",
        ]
        if book.isbn:
            parts.append(f"ISBN: {book.isbn}")
        if book.publisher:
            parts.append(f"Publisher: {book.publisher}")
        if book.publication_year:
            parts.append(f"Publication Year: {book.publication_year}")
        if book.category:
            parts.append(f"Category: {book.category}")
        if book.description:
            parts.append(f"Description: {book.description}")
        parts.append(f"Available Copies: {book.available_copies} of {book.total_copies}")

        return "\n".join(parts)

    async def search_books(
        self, query: str, top_k: int = 10, tenant_id: UUID | None = None
    ) -> list[dict[str, Any]]:
        from app.ai.embeddings import EmbeddingService
        from app.ai.vectorstore import get_vector_store

        vs = get_vector_store()
        embeddings = EmbeddingService()

        query_embedding = await embeddings.embed_query(query)

        filters = {"category": "book"}
        if tenant_id:
            filters["tenant_id"] = str(tenant_id)

        results = await vs.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter=filters,
        )

        return [
            {
                "id": r["id"],
                "text": r["text"],
                "score": r["score"],
                "metadata": r["metadata"],
            }
            for r in results
        ]
