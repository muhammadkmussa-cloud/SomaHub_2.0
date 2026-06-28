"""
Text extraction from multiple file formats.
Supports: PDF, DOCX, TXT, MD, CSV, JSON, EPUB, Images (OCR via Ollama vision).
"""

import io
import logging
from pathlib import Path

from app.ai.config import ai_settings
from app.ai.ollama_client import OllamaClient

logger = logging.getLogger("somahub.ai.text_extractor")


class TextExtractionError(Exception):
    pass


class TextExtractor:
    def __init__(self, ollama_client: OllamaClient | None = None):
        self.ollama = ollama_client or OllamaClient()

    async def extract(self, content: bytes, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        extractors = {
            ".pdf": self._extract_pdf,
            ".docx": self._extract_docx,
            ".txt": self._extract_text,
            ".md": self._extract_text,
            ".csv": self._extract_text,
            ".json": self._extract_text,
            ".epub": self._extract_epub,
            ".png": self._extract_image,
            ".jpg": self._extract_image,
            ".jpeg": self._extract_image,
            ".gif": self._extract_image,
            ".bmp": self._extract_image,
            ".webp": self._extract_image,
            ".tiff": self._extract_image,
        }

        extractor = extractors.get(ext)
        if not extractor:
            raise TextExtractionError(f"Unsupported file type: {ext}")

        return await extractor(content)

    async def _extract_text(self, content: bytes) -> str:
        return content.decode("utf-8", errors="replace")

    async def _extract_pdf(self, content: bytes) -> str:
        try:
            import PyPDF2

            reader = PyPDF2.PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
        except ImportError:
            logger.warning("PyPDF2 not available, trying pypdf")
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(content))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
        except ImportError:
            raise TextExtractionError(
                "PDF extraction requires PyPDF2 or pypdf library"
            )

    async def _extract_docx(self, content: bytes) -> str:
        try:
            from docx import Document

            doc = Document(io.BytesIO(content))
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            raise TextExtractionError("DOCX extraction requires python-docx library")

    async def _extract_epub(self, content: bytes) -> str:
        try:
            import ebooklib
            from ebooklib import epub
            from bs4 import BeautifulSoup

            book = epub.read_epub(io.BytesIO(content))
            texts = []
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    texts.append(soup.get_text(separator="\n"))
            return "\n\n".join(texts)
        except ImportError:
            raise TextExtractionError(
                "EPUB extraction requires EbookLib and BeautifulSoup4"
            )

    async def _extract_image(self, content: bytes) -> str:
        if not ai_settings.OCR_ENABLED:
            raise TextExtractionError("OCR is disabled")

        import base64

        image_b64 = base64.b64encode(content).decode("utf-8")
        prompt = (
            "Extract all text content from this image. "
            "Return only the text you find, preserving structure where possible."
        )
        try:
            text = await self.ollama.vision(image_b64, prompt)
            return text.strip()
        except Exception as e:
            logger.error("OCR extraction failed: %s", e)
            raise TextExtractionError(f"OCR failed: {e}")

    async def extract_metadata(self, content: bytes, filename: str) -> dict:
        ext = Path(filename).suffix.lower()
        metadata: dict = {
            "source": filename,
            "type": ext.lstrip("."),
            "size_bytes": len(content),
        }
        return metadata
