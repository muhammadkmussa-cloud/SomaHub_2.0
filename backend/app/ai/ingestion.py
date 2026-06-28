"""
Document ingestion pipeline.
Detects file type, extracts text, chunks, generates embeddings, stores in vector DB.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any

from app.ai.chunker import TextChunker
from app.ai.config import ai_settings
from app.ai.embeddings import EmbeddingService
from app.ai.text_extractor import TextExtractor
from app.ai.vectorstore import IVectorStore, get_vector_store

logger = logging.getLogger("somahub.ai.ingestion")


class IngestionPipeline:
    def __init__(
        self,
        vector_store: IVectorStore | None = None,
        embedding_service: EmbeddingService | None = None,
        text_extractor: TextExtractor | None = None,
        chunker: TextChunker | None = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_service = embedding_service or EmbeddingService()
        self.text_extractor = text_extractor or TextExtractor()
        self.chunker = chunker or TextChunker()

    def _compute_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def _generate_id(self, content_hash: str, chunk_index: int) -> str:
        return f"{content_hash}_{chunk_index}"

    async def ingest(
        self,
        content: bytes,
        filename: str,
        source_type: str = "upload",
        extra_metadata: dict[str, Any] | None = None,
    ) -> int:
        content_hash = self._compute_hash(content)

        text = await self.text_extractor.extract(content, filename)
        if not text.strip():
            logger.warning("No text extracted from %s", filename)
            return 0

        file_metadata = await self.text_extractor.extract_metadata(content, filename)
        base_metadata = {
            **file_metadata,
            "content_hash": content_hash,
            "source_type": source_type,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            **(extra_metadata or {}),
        }

        chunks = self.chunker.chunk(text, base_metadata)
        if not chunks:
            return 0

        chunk_texts = [c["text"] for c in chunks]
        chunk_metas = [c["metadata"] for c in chunks]
        chunk_ids = [
            self._generate_id(content_hash, i) for i in range(len(chunks))
        ]

        embeddings = await self.embedding_service.embed_batch(chunk_texts)
        if not embeddings:
            logger.error("Failed to generate embeddings for %s", filename)
            return 0

        existing_ids = await self._find_existing(content_hash)
        if existing_ids:
            await self.vector_store.delete(existing_ids)

        await self.vector_store.add_texts(
            texts=chunk_texts,
            embeddings=embeddings,
            metadatas=chunk_metas,
            ids=chunk_ids,
        )

        logger.info(
            "Ingested %s → %d chunks (hash=%s)", filename, len(chunks), content_hash[:12]
        )
        return len(chunks)

    async def _find_existing(self, content_hash: str) -> list[str]:
        try:
            results = await self.vector_store.similarity_search(
                query_embedding=[0.0] * ai_settings.EMBEDDING_DIMENSIONS,
                top_k=1000,
                score_threshold=-1.0,
                filter={"content_hash": content_hash},
            )
            return [r["id"] for r in results if r["metadata"].get("content_hash") == content_hash]
        except Exception:
            return []

    async def ingest_text(
        self,
        text: str,
        source_id: str,
        source_type: str = "text",
        extra_metadata: dict[str, Any] | None = None,
    ) -> int:
        content_bytes = text.encode("utf-8")
        content_hash = self._compute_hash(content_bytes)

        base_metadata = {
            "source": source_id,
            "type": "text",
            "size_bytes": len(content_bytes),
            "content_hash": content_hash,
            "source_type": source_type,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            **(extra_metadata or {}),
        }

        chunks = self.chunker.chunk(text, base_metadata)
        if not chunks:
            return 0

        chunk_texts = [c["text"] for c in chunks]
        chunk_metas = [c["metadata"] for c in chunks]
        chunk_ids = [
            self._generate_id(content_hash, i) for i in range(len(chunks))
        ]

        embeddings = await self.embedding_service.embed_batch(chunk_texts)
        if not embeddings:
            return 0

        existing_ids = await self._find_existing(content_hash)
        if existing_ids:
            await self.vector_store.delete(existing_ids)

        await self.vector_store.add_texts(
            texts=chunk_texts,
            embeddings=embeddings,
            metadatas=chunk_metas,
            ids=chunk_ids,
        )

        logger.info(
            "Ingested text %s → %d chunks (hash=%s)",
            source_id,
            len(chunks),
            content_hash[:12],
        )
        return len(chunks)
