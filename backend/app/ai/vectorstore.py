"""
Vector store abstraction — ChromaDB implementation.
Pluggable design — swap to Qdrant/pgvector later by implementing IVectorStore.
"""

import logging
import uuid
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.ai.config import ai_settings

logger = logging.getLogger("somahub.ai.vectorstore")


class IVectorStore:
    async def add_texts(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]: ...

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        score_threshold: float | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]: ...

    async def delete(self, ids: list[str]) -> None: ...

    async def count(self) -> int: ...

    async def health(self) -> bool: ...


class ChromaVectorStore(IVectorStore):
    def __init__(self):
        self.collection_name = ai_settings.VECTOR_STORE_COLLECTION
        self._client = chromadb.PersistentClient(
            path=ai_settings.VECTOR_STORE_PATH,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _get_collection(self):
        return self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    async def add_texts(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        if not texts or not embeddings:
            return []

        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        if metadatas is None:
            metadatas = [{} for _ in texts]

        collection = self._get_collection()
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info("Added %d documents to vector store", len(texts))
        return ids

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int | None = None,
        score_threshold: float | None = None,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        k = top_k or ai_settings.RETRIEVAL_TOP_K
        threshold = score_threshold or ai_settings.RETRIEVAL_SCORE_THRESHOLD

        collection = self._get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter,
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i] if results.get("distances") else 0
                score = 1.0 - distance  # cosine distance → similarity
                if score < threshold:
                    continue
                documents.append(
                    {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": score,
                    }
                )

        return documents

    async def delete(self, ids: list[str]) -> None:
        collection = self._get_collection()
        collection.delete(ids=ids)
        logger.info("Deleted %d documents from vector store", len(ids))

    async def delete_by_filter(self, filter: dict[str, Any]) -> None:
        collection = self._get_collection()
        collection.delete(where=filter)

    async def count(self) -> int:
        collection = self._get_collection()
        return collection.count()

    async def health(self) -> bool:
        try:
            self._client.heartbeat()
            return True
        except Exception as e:
            logger.error("Vector store health check failed: %s", e)
            return False


def get_vector_store() -> IVectorStore:
    store_type = ai_settings.VECTOR_STORE_TYPE
    if store_type == "chromadb":
        return ChromaVectorStore()
    raise ValueError(f"Unknown vector store type: {store_type}")
