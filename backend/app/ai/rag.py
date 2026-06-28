"""
RAG pipeline — retrieve relevant chunks, construct context, generate grounded answer.
"""

import json
import logging
from typing import AsyncGenerator

from app.ai.config import ai_settings
from app.ai.embeddings import EmbeddingService
from app.ai.ollama_client import OllamaClient
from app.ai.vectorstore import IVectorStore, get_vector_store

logger = logging.getLogger("somahub.ai.rag")


SYSTEM_PROMPT = """You are SomaBot, an intelligent AI assistant for SomaHub — a library management platform.

Your role is to help users with:
- Navigating the SomaHub application
- Finding and understanding books in the library catalog
- Explaining borrowing procedures and library policies
- Answering questions about using the platform

Guidelines:
1. Answer based ONLY on the provided context. If the context doesn't contain the answer, say so clearly.
2. Cite your sources by mentioning the document or page name when possible.
3. Be concise, friendly, and helpful.
4. If you're unsure, say you don't know rather than guessing.
5. Do NOT reveal sensitive information like passwords, API keys, or internal configuration.
6. Keep answers in the same language as the question."""


class RAGPipeline:
    def __init__(
        self,
        vector_store: IVectorStore | None = None,
        embedding_service: EmbeddingService | None = None,
        ollama_client: OllamaClient | None = None,
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_service = embedding_service or EmbeddingService()
        self.ollama = ollama_client or OllamaClient()
        self.top_k = ai_settings.RETRIEVAL_TOP_K

    async def query(
        self,
        question: str,
        history: list[dict] | None = None,
        stream: bool = False,
        filter: dict | None = None,
    ) -> dict | AsyncGenerator[str, None]:
        query_embedding = await self.embedding_service.embed_query(question)

        results = await self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=self.top_k,
            filter=filter,
        )

        if stream:
            return self._stream_response(question, results, history)

        context = self._build_context(results)
        answer = await self._generate_answer(question, context, history)

        return {
            "answer": answer,
            "citations": self._extract_citations(results),
            "sources": [r["metadata"] for r in results],
            "context_used": bool(results),
        }

    def _stream_response(
        self,
        question: str,
        results: list[dict],
        history: list[dict] | None = None,
    ):
        context = self._build_context(results)
        citations = self._extract_citations(results)

        async def generate():
            citation_text = json.dumps(citations) if citations else "[]"
            yield json.dumps({"type": "citations", "data": citations}) + "\n"

            system = SYSTEM_PROMPT
            if context:
                system += f"\n\nCurrent context available: {len(results)} relevant documents."

            async for chunk in self.ollama.chat_with_context(
                system_prompt=system,
                user_message=question,
                context=context,
                history=history,
                stream=True,
            ):
                if isinstance(chunk, str):
                    yield json.dumps({"type": "token", "data": chunk}) + "\n"

            yield json.dumps({"type": "done", "data": True}) + "\n"

        return generate()

    async def query_no_context(
        self,
        question: str,
        history: list[dict] | None = None,
        stream: bool = False,
    ) -> dict | AsyncGenerator[str, None]:
        if stream:
            async def generate():
                async for chunk in self.ollama.chat_with_context(
                    system_prompt=SYSTEM_PROMPT,
                    user_message=question,
                    context=None,
                    history=history,
                    stream=True,
                ):
                    if isinstance(chunk, str):
                        yield json.dumps({"type": "token", "data": chunk}) + "\n"
                yield json.dumps({"type": "done", "data": True}) + "\n"
            return generate()

        result = await self.ollama.chat_with_context(
            system_prompt=SYSTEM_PROMPT,
            user_message=question,
            context=None,
            history=history,
        )
        if isinstance(result, dict):
            return {
                "answer": result.get("content", ""),
                "citations": [],
                "sources": [],
                "context_used": False,
            }
        return {"answer": "", "citations": [], "sources": [], "context_used": False}

    async def _generate_answer(
        self,
        question: str,
        context: str,
        history: list[dict] | None = None,
    ) -> str:
        result = await self.ollama.chat_with_context(
            system_prompt=SYSTEM_PROMPT,
            user_message=question,
            context=context,
            history=history,
        )
        if isinstance(result, dict):
            return result.get("content", "")
        return ""

    def _build_context(self, results: list[dict]) -> str:
        if not results:
            return ""

        context_parts = []
        for i, r in enumerate(results, 1):
            meta = r.get("metadata", {})
            source = meta.get("source", "Unknown source")
            context_parts.append(
                f"[Document {i}] Source: {source}\n{r.get('text', '')}"
            )

        return "\n\n---\n\n".join(context_parts)

    def _extract_citations(self, results: list[dict]) -> list[dict]:
        citations = []
        seen = set()
        for r in results:
            meta = r.get("metadata", {})
            source = meta.get("source", "Unknown")
            text = r.get("text", "")[:150]
            key = f"{source}:{text[:50]}"
            if key not in seen:
                seen.add(key)
                citations.append(
                    {
                        "source": source,
                        "type": meta.get("type", "document"),
                        "text_snippet": text,
                        "score": round(r.get("score", 0), 3),
                    }
                )
        return citations
