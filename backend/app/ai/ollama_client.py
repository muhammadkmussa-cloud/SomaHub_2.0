"""
Ollama HTTP client for chat, embeddings, and vision.
Pluggable design — swap to OpenAI/anthropic later by implementing the same interface.
"""

import json
import logging
from typing import AsyncGenerator

import httpx

from app.ai.config import ai_settings

logger = logging.getLogger("somahub.ai.ollama")


class OllamaError(Exception):
    pass


class OllamaClient:
    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        self.base_url = (base_url or ai_settings.OLLAMA_HOST).rstrip("/")
        self.timeout = timeout or ai_settings.OLLAMA_TIMEOUT

    async def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}/api/{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                raise OllamaError(
                    f"Ollama {endpoint} failed: {resp.status_code} {resp.text[:200]}"
                )
            return resp.json()

    async def _post_stream(
        self, endpoint: str, payload: dict
    ) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/api/{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream("POST", url, json=payload) as resp:
                if resp.status_code != 200:
                    raise OllamaError(
                        f"Ollama {endpoint} stream failed: {resp.status_code}"
                    )
                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue

    async def chat(
        self, messages: list[dict], stream: bool = False
    ) -> dict | AsyncGenerator[str, None]:
        payload = {
            "model": ai_settings.CHAT_MODEL,
            "messages": messages,
            "options": {
                "temperature": ai_settings.CHAT_TEMPERATURE,
                "num_predict": ai_settings.CHAT_MAX_TOKENS,
                "top_p": ai_settings.CHAT_TOP_P,
            },
            "stream": stream,
        }

        if stream:
            return self._post_stream("chat", payload)

        result = await self._post("chat", payload)
        return {
            "content": result.get("message", {}).get("content", ""),
            "done": result.get("done", True),
        }

    async def chat_with_context(
        self,
        system_prompt: str,
        user_message: str,
        context: str | None = None,
        history: list[dict] | None = None,
        stream: bool = False,
    ) -> dict | AsyncGenerator[str, None]:
        messages: list[dict] = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history[-ai_settings.MAX_HISTORY_LENGTH * 2 :])

        if context:
            user_content = f"""Context information:
{context}

User question: {user_message}

Answer based on the context. If you cannot find the answer in the context, say so."""
        else:
            user_content = user_message

        messages.append({"role": "user", "content": user_content})

        return await self.chat(messages, stream=stream)

    async def generate(self, prompt: str, system: str | None = None, stream: bool = False) -> dict | AsyncGenerator[str, None]:
        payload = {
            "model": ai_settings.CHAT_MODEL,
            "prompt": prompt,
            "options": {
                "temperature": ai_settings.CHAT_TEMPERATURE,
                "num_predict": ai_settings.CHAT_MAX_TOKENS,
            },
            "stream": stream,
        }
        if system:
            payload["system"] = system

        if stream:
            return self._post_stream("generate", payload)

        result = await self._post("generate", payload)
        return {
            "content": result.get("response", ""),
            "done": result.get("done", True),
        }

    async def vision(
        self, image_base64: str, prompt: str, system: str | None = None
    ) -> str:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})

        messages.append(
            {
                "role": "user",
                "content": prompt,
                "images": [image_base64],
            }
        )

        payload = {
            "model": ai_settings.VISION_MODEL,
            "messages": messages,
            "options": {
                "temperature": ai_settings.VISION_TEMPERATURE,
                "num_predict": ai_settings.VISION_MAX_TOKENS,
            },
        }

        result = await self._post("chat", payload)
        return result.get("message", {}).get("content", "")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        payload = {
            "model": ai_settings.EMBEDDING_MODEL,
            "input": texts,
        }
        result = await self._post("embed", payload)
        return result.get("embeddings", [])

    async def health(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    available = [m["name"] for m in models]
                    return {
                        "status": "ok",
                        "models": available,
                    }
                return {"status": "error", "detail": resp.text[:200]}
        except Exception as e:
            return {"status": "error", "detail": str(e)}

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            pass
        return []

    async def pull_model(self, model: str) -> AsyncGenerator[dict, None]:
        url = f"{self.base_url}/api/pull"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json={"name": model}) as resp:
                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
