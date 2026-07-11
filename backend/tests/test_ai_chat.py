"""Unit tests for the AI chatbot API router and Ollama stream parser."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.ai.ollama_client import OllamaClient


@pytest.mark.asyncio
async def test_chat_no_stream(async_client, auth_headers):
    """POST /api/v1/ai/chat with stream=False should return non-stream response."""
    mock_rag_result = {
        "answer": "This is a non-stream response.",
        "citations": [{"source": "docs", "text_snippet": "info"}],
        "sources": [{"source": "docs"}],
        "context_used": True,
    }

    mock_rag = MagicMock()
    mock_rag.query = AsyncMock(return_value=mock_rag_result)

    from app.main import app
    from app.ai.router import get_rag
    app.dependency_overrides[get_rag] = lambda: mock_rag

    try:
        response = await async_client.post(
            "/api/v1/ai/chat",
            json={"message": "test question", "stream": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "This is a non-stream response."
        assert data["context_used"] is True
        assert len(data["citations"]) == 1
    finally:
        del app.dependency_overrides[get_rag]


@pytest.mark.asyncio
async def test_chat_stream(async_client, auth_headers):
    """POST /api/v1/ai/chat with stream=True should stream RAG generator chunks."""
    async def mock_generator():
        yield '{"type": "citations", "data": []}\n'
        yield '{"type": "token", "data": "Hello"}\n'
        yield '{"type": "token", "data": " World"}\n'
        yield '{"type": "done", "data": true}\n'

    mock_rag = MagicMock()
    mock_rag.query = AsyncMock(return_value=mock_generator())

    from app.main import app
    from app.ai.router import get_rag
    app.dependency_overrides[get_rag] = lambda: mock_rag

    try:
        response = await async_client.post(
            "/api/v1/ai/chat",
            json={"message": "test question", "stream": True},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-ndjson"

        # Read the streamed body chunks
        body = b""
        async for chunk in response.aiter_bytes():
            body += chunk

        lines = body.decode().strip().split("\n")
        assert len(lines) == 4
        assert json.loads(lines[1])["data"] == "Hello"
        assert json.loads(lines[2])["data"] == " World"
    finally:
        del app.dependency_overrides[get_rag]


@pytest.mark.asyncio
async def test_ollama_client_post_stream_chat():
    """Verify OllamaClient._post_stream correctly extracts chunk values from the 'message' object for /api/chat."""
    client = OllamaClient(base_url="http://mock-ollama")

    stream_lines = [
        '{"message": {"role": "assistant", "content": "Hello"}, "done": false}\n',
        '{"message": {"role": "assistant", "content": " World"}, "done": false}\n',
        '{"done": true}\n',
    ]

    async def mock_aiter_lines():
        for line in stream_lines:
            yield line

    with patch("httpx.AsyncClient.stream") as mock_stream:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.aiter_lines = mock_aiter_lines

        class MockAsyncContextManager:
            async def __aenter__(self):
                return mock_resp

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        mock_stream.return_value = MockAsyncContextManager()

        chunks = []
        async for chunk in client._post_stream("chat", {}):
            chunks.append(chunk)

        assert chunks == ["Hello", " World"]
