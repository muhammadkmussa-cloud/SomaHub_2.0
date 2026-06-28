"""
OCR pipeline using Ollama vision models.
Replaces Gemini entirely. Extracts structured book metadata from cover/page images.
"""

import base64
import json
import logging
import re
from typing import Any

from app.ai.config import ai_settings
from app.ai.ollama_client import OllamaClient

logger = logging.getLogger("somahub.ai.ocr")


class OCRPipeline:
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()
        self.vision_model = ai_settings.VISION_MODEL

    async def extract_text(self, image_content: bytes) -> str:
        image_b64 = base64.b64encode(image_content).decode("utf-8")
        prompt = (
            "Extract all visible text from this image. "
            "Return the exact text content you see, preserving structure."
        )
        return await self.client.vision(image_b64, prompt)

    async def extract_book_metadata(self, image_content: bytes) -> dict[str, Any]:
        image_b64 = base64.b64encode(image_content).decode("utf-8")

        system_prompt = (
            "You are a professional book cataloging assistant. "
            "Extract book metadata from the image and return ONLY valid JSON."
        )

        user_prompt = """Analyze this book cover or page image and extract metadata.
Return ONLY a JSON object with these fields (use null for unknown):
{
  "title": "string",
  "subtitle": "string or null",
  "authors": ["string"],
  "publisher": "string or null",
  "isbn": "string or null",
  "publication_year": number or null,
  "edition": "string or null",
  "language": "string or null",
  "categories": ["string"],
  "description": "string or null",
  "subjects": ["string"]
}"""

        raw = await self.client.vision(image_b64, user_prompt, system_prompt)
        return self._parse_metadata(raw)

    async def extract_isbn(self, image_content: bytes) -> str | None:
        image_b64 = base64.b64encode(image_content).decode("utf-8")
        prompt = (
            "Extract any ISBN-10 or ISBN-13 barcode or number from this image. "
            "Return only the ISBN number, nothing else."
        )
        result = await self.client.vision(image_b64, prompt)
        isbn = re.sub(r"[^0-9Xx]", "", result.strip())
        return isbn if len(isbn) in (10, 13) else None

    async def generate_description(self, image_content: bytes) -> str:
        image_b64 = base64.b64encode(image_content).decode("utf-8")
        prompt = (
            "Write a professional, concise book description (2-4 sentences) "
            "based on this book cover image. Include the topic, target audience, "
            "and key themes."
        )
        return await self.client.vision(image_b64, prompt)

    def _parse_metadata(self, raw: str) -> dict[str, Any]:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                logger.warning("Failed to parse metadata JSON, extracting fields manually")

        metadata: dict[str, Any] = {
            "title": None,
            "subtitle": None,
            "authors": [],
            "publisher": None,
            "isbn": None,
            "publication_year": None,
            "edition": None,
            "language": None,
            "categories": [],
            "description": None,
            "subjects": [],
        }

        lines = raw.strip().split("\n")
        for line in lines:
            lower = line.lower()
            for field in metadata:
                if field in ("authors", "categories", "subjects"):
                    continue
                if f"{field}:" in lower:
                    val = line.split(":", 1)[1].strip().strip('"').strip(",")
                    if val and val != "null":
                        metadata[field] = val

        authors_match = re.search(r"authors?:?\s*\[?(.*?)\]?", raw, re.IGNORECASE | re.DOTALL)
        if authors_match:
            authors_str = authors_match.group(1)
            metadata["authors"] = [
                a.strip().strip('"').strip("'")
                for a in re.split(r'[,"]+', authors_str)
                if a.strip()
            ]

        return metadata

    async def process_book_image(
        self, image_content: bytes
    ) -> dict[str, Any]:
        metadata = await self.extract_book_metadata(image_content)

        if not metadata.get("description"):
            metadata["description"] = await self.generate_description(image_content)

        if not metadata.get("isbn"):
            metadata["isbn"] = await self.extract_isbn(image_content)

        return metadata
