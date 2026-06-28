"""
AI subsystem configuration.
All models, hosts, chunking, and vector store settings in one place.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="AI_",
    )

    # ── Ollama ────────────────────────────────────────────────────────
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 120

    # ── Chat model ────────────────────────────────────────────────────
    CHAT_MODEL: str = "llama3:latest"
    CHAT_TEMPERATURE: float = 0.7
    CHAT_MAX_TOKENS: int = 2048
    CHAT_TOP_P: float = 0.9

    # ── Embedding model ───────────────────────────────────────────────
    EMBEDDING_MODEL: str = "nomic-embed-text"
    EMBEDDING_DIMENSIONS: int = 768

    # ── Vision model (OCR) ────────────────────────────────────────────
    VISION_MODEL: str = "granite-vision:latest"
    VISION_TEMPERATURE: float = 0.2
    VISION_MAX_TOKENS: int = 4096

    # ── Chunking ──────────────────────────────────────────────────────
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # ── Retrieval ─────────────────────────────────────────────────────
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SCORE_THRESHOLD: float = 0.65

    # ── Vector store ──────────────────────────────────────────────────
    VECTOR_STORE_TYPE: str = "chromadb"
    VECTOR_STORE_PATH: str = str(Path("data/vectordb"))
    VECTOR_STORE_COLLECTION: str = "somahub_knowledge"

    # ── Ingestion ─────────────────────────────────────────────────────
    INGESTION_BATCH_SIZE: int = 50
    INGESTION_MAX_FILE_SIZE_MB: int = 50

    # ── OCR ───────────────────────────────────────────────────────────
    OCR_ENABLED: bool = True
    OCR_IMAGE_MAX_SIZE: int = 2048

    # ── App knowledge ─────────────────────────────────────────────────
    APP_KNOWLEDGE_ENABLED: bool = True

    # ── Chat history ──────────────────────────────────────────────────
    MAX_HISTORY_LENGTH: int = 20

    # ── Logging ───────────────────────────────────────────────────────
    AI_LOG_LEVEL: str = "INFO"


@lru_cache()
def get_ai_settings() -> AISettings:
    return AISettings()


ai_settings = get_ai_settings()
