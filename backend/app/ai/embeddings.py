"""
Embedding service — generates vector embeddings via Ollama.
"""

import logging
from functools import lru_cache

from app.ai.config import ai_settings
from app.ai.ollama_client import OllamaClient

logger = logging.getLogger("somahub.ai.embeddings")


class EmbeddingService:
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()
        self.model = ai_settings.EMBEDDING_MODEL

    async def embed(self, text: str) -> list[float]:
        embeddings = await self.embed_batch([text])
        return embeddings[0] if embeddings else []

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            return await self.client.embed(texts)
        except Exception as e:
            logger.error("Embedding failed: %s", e)
            raise

    @lru_cache(maxsize=512)
    async def embed_cached(self, text: str) -> list[float]:
        return await self.embed(text)

    async def embed_query(self, query: str) -> list[float]:
        return await self.embed(query)
