"""
SomaHub Enterprise — FastAPI application entry point.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.redis import close_redis, init_redis
from app.modules.analytics.router import router as analytics_router
from app.modules.auth.router import router as auth_router
from app.modules.bookmarks.router import router as bookmark_router
from app.modules.books.router import copy_router as book_copy_router
from app.modules.books.router import router as book_router
from app.modules.borrowers.router import router as borrower_router
from app.modules.debug.router import router as debug_router
from app.modules.ebook_purchases.router import router as ebook_purchase_router
from app.modules.ebooks.router import router as ebook_router
from app.modules.favorites.router import router as favorite_router
from app.modules.fines.router import router as fine_router
from app.modules.libraries.router import router as library_router
from app.modules.loans.router import router as loan_router
from app.modules.notifications.router import router as notification_router
from app.modules.payments.router import router as payment_router
from app.modules.reading_progress.router import router as reading_progress_router
from app.modules.reviews.router import router as review_router
from app.modules.subscriptions.router import router as subscription_router
from app.modules.tenants.router import router as tenant_router
from app.modules.users.router import router as user_router

# Setup application logging
setup_logging()
logger = logging.getLogger("somahub")


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("%s v%s starting", settings.APP_NAME, settings.APP_VERSION)
    await init_redis()
    yield
    logger.info("Shutting down")
    await close_redis()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-tenant Library Management & Digital Reading SaaS",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(tenant_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(book_router, prefix=API_PREFIX)
app.include_router(book_copy_router, prefix=API_PREFIX)
app.include_router(borrower_router, prefix=API_PREFIX)
app.include_router(loan_router, prefix=API_PREFIX)
app.include_router(fine_router, prefix=API_PREFIX)
app.include_router(notification_router, prefix=API_PREFIX)
app.include_router(library_router, prefix=API_PREFIX)
app.include_router(ebook_router, prefix=API_PREFIX)
app.include_router(ebook_purchase_router, prefix=API_PREFIX)
app.include_router(reading_progress_router, prefix=API_PREFIX)
app.include_router(bookmark_router, prefix=API_PREFIX)
app.include_router(favorite_router, prefix=API_PREFIX)
app.include_router(review_router, prefix=API_PREFIX)
app.include_router(payment_router, prefix=API_PREFIX)
app.include_router(subscription_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)

# Development-only debug routes
if settings.DEBUG:
    app.include_router(debug_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    from app.core.database import check_db_connection
    from app.core.redis import check_db_connection as check_redis

    db_ok = await check_db_connection()
    redis_ok = await check_redis()

    migration_head = None
    try:
        alembic_cfg = Config("alembic.ini")
        migration_head = ScriptDirectory.from_config(alembic_cfg).get_current_head()
    except Exception:
        migration_head = "unknown"

    return {
        "status": "healthy" if db_ok and redis_ok else "degraded",
        "version": settings.APP_VERSION,
        "migration_head": migration_head,
        "services": {
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
        },
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }
