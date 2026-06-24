"""
SomaHub application configuration.
Uses pydantic-settings for environment variable management.
"""

import logging
import warnings
from functools import lru_cache
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────
    APP_NAME: str = "SomaHub Enterprise"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | testing | staging | production
    DEBUG: bool = True

    # ── Security ─────────────────────────────────────────────────────
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    EMAIL_VERIFY_TOKEN_EXPIRE_HOURS: int = 24
    AUTH_RATE_LIMIT: int = 10
    AUTH_RATE_WINDOW_SECONDS: int = 60

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/somahub"

    # ── Redis ─────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── CORS ──────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # ── Object Storage (Supabase / S3-compatible) ─────────────────────
    STORAGE_PROVIDER: str = "local"
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_BUCKET_EBOOKS: str = "ebooks"
    SUPABASE_BUCKET_COVERS: str = "covers"
    SUPABASE_BUCKET_AVATARS: str = "avatars"
    SUPABASE_BUCKET_OCR: str = "ocr-uploads"
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    S3_BUCKET_EBOOKS: str = "somahub-ebooks"
    S3_BUCKET_COVERS: str = "somahub-covers"
    S3_BUCKET_AVATARS: str = "somahub-avatars"

    # ── Email (Resend) ────────────────────────────────────────────────
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@somahub.io"
    EMAIL_FROM_NAME: str = "SomaHub"

    # ── OCR (Gemini) ──────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""

    # ── Payments ──────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_WEBHOOK_SECRET: str = ""

    # ── Search (Meilisearch / Elasticsearch) ──────────────────────────
    SEARCH_PROVIDER: str = "basic"
    MEILISEARCH_URL: str = "http://localhost:7700"
    MEILISEARCH_API_KEY: str = ""
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_API_KEY: str = ""

    # ── Analytics ─────────────────────────────────────────────────────
    ANALYTICS_ENABLED: bool = True

    # ── Frontend URL (for email links) ────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def cookie_secure(self) -> bool:
        return self.APP_ENV in ("production", "staging")

    @model_validator(mode="after")
    def validate_environment(self) -> "Settings":
        if self.APP_ENV not in ("development", "testing", "staging", "production"):
            raise ValueError(f"Invalid APP_ENV: {self.APP_ENV}")

        if self.APP_ENV in ("staging", "production") and not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY must be set when APP_ENV is staging or production."
            )

        if self.APP_ENV in ("development", "testing") and not self.SECRET_KEY:
            self.SECRET_KEY = "dev-insecure-secret-key-for-local-only-32chars"

        if self.APP_ENV == "production" and self.DEBUG:
            raise ValueError("DEBUG must be false when APP_ENV is production.")

        if self.APP_ENV == "development":
            if not self.SECRET_KEY:
                warnings.warn(
                    "SECRET_KEY is not set — using insecure development default.",
                    stacklevel=2,
                )
            if not self.RESEND_API_KEY:
                logger.warning(
                    "RESEND_API_KEY is not set — emails will print to console."
                )

        return self


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()
