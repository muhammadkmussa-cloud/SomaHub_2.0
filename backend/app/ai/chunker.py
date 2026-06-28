"""
Text chunking — splits documents into semantic chunks for embedding.
"""

import logging
import re
from typing import Generator

from app.ai.config import ai_settings

logger = logging.getLogger("somahub.ai.chunker")


class TextChunker:
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or ai_settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or ai_settings.CHUNK_OVERLAP

    def chunk(self, text: str, metadata: dict | None = None) -> list[dict]:
        chunks = []
        for i, chunk_text in enumerate(self._split_text(text)):
            chunk_meta = dict(metadata or {})
            chunk_meta["chunk_index"] = i
            chunks.append(
                {
                    "text": chunk_text.strip(),
                    "metadata": chunk_meta,
                }
            )
        return chunks

    def _split_text(self, text: str) -> Generator[str, None, None]:
        if not text.strip():
            return

        paragraphs = re.split(r"\n\s*\n", text)
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)

            if current_size + para_len <= self.chunk_size:
                current_chunk.append(para)
                current_size += para_len + 1
            else:
                if current_chunk:
                    yield "\n\n".join(current_chunk)

                if para_len > self.chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    sub_chunk = []
                    sub_size = 0
                    for sent in sentences:
                        sent_len = len(sent)
                        if sub_size + sent_len <= self.chunk_size:
                            sub_chunk.append(sent)
                            sub_size += sent_len + 1
                        else:
                            if sub_chunk:
                                yield " ".join(sub_chunk)
                            sub_chunk = [sent]
                            sub_size = sent_len
                    if sub_chunk:
                        overlap_text = sub_chunk[-1] if sub_chunk else ""
                        yield " ".join(sub_chunk)
                        current_chunk = []
                        current_size = 0
                        if self.chunk_overlap > 0 and overlap_text:
                            current_chunk = [overlap_text]
                            current_size = len(overlap_text)
                else:
                    yield para
                    current_chunk = []
                    current_size = 0

        if current_chunk:
            yield "\n\n".join(current_chunk)

    def chunk_with_overlap(self, text: str, metadata: dict | None = None) -> list[dict]:
        chunks = list(self._split_text(text))
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk_meta = dict(metadata or {})
            chunk_meta["chunk_index"] = i
            result.append(
                {
                    "text": chunk_text.strip(),
                    "metadata": chunk_meta,
                }
            )
        return result
