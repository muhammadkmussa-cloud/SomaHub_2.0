"""
SomaHub Enterprise — FastAPI application entry point.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.redis import close_redis, init_redis
from app.ai.router import router as ai_router
from app.modules.analytics.router import router as analytics_router
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.bookmarks.router import router as bookmark_router
from app.modules.books.router import copy_router as book_copy_router
from app.modules.books.router import router as book_router
from app.modules.bookstore.router import router as bookstore_router
from app.modules.borrowers.router import router as borrower_router
from app.modules.debug.router import router as debug_router
from app.modules.ebook_purchases.router import router as ebook_purchase_router
from app.modules.ebooks.router import router as ebook_router
from app.modules.favorites.router import router as favorite_router
from app.modules.fines.router import router as fine_router
from app.modules.libraries.router import router as library_router
from app.modules.loans.router import router as loan_router
from app.modules.notifications.router import router as notification_router
from app.modules.ocr.router import router as ocr_router
from app.modules.payments.router import router as payment_router
from app.modules.reader.router import router as reader_router
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

    # Auto-create dev superadmin in development mode
    if settings.DEBUG and settings.APP_ENV == "development":
        try:
            from app.core.database import async_session_factory
            from app.core.security import hash_password
            from app.modules.auth.models import User
            from app.modules.auth.repository import UserRepository
            from uuid import uuid4

            async with async_session_factory() as dev_session:
                repo = UserRepository(dev_session)
                existing = await repo.get_by_email("admin@somahub.io")
                if not existing:
                    dev_user = User(
                        id=uuid4(),
                        tenant_id=None,
                        email="admin@somahub.io",
                        username="superadmin",
                        hashed_password=hash_password("Admin123!"),
                        role="super_admin",
                        is_active=True,
                        is_email_verified=True,
                    )
                    dev_session.add(dev_user)
                    await dev_session.commit()
                    logger.info("Dev superadmin created: admin@somahub.io / Admin123!")
                else:
                    logger.debug("Dev superadmin already exists")
        except Exception as e:
            logger.warning("Dev superadmin creation skipped: %s", e)

    # Auto-index app knowledge on startup
    try:
        from app.ai.app_knowledge import AppKnowledgeBase
        from app.ai.config import ai_settings

        if ai_settings.APP_KNOWLEDGE_ENABLED:
            kb = AppKnowledgeBase()
            if not kb.is_indexed:
                total = await kb.index_all()
                logger.info("App knowledge base indexed: %d entries", total)
    except Exception as e:
        logger.warning("App knowledge indexing skipped: %s", e)

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

# ── Static file serving (uploads: PDFs, covers, avatars) ──────────────────────
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(ai_router, prefix=API_PREFIX)
app.include_router(audit_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(tenant_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(book_router, prefix=API_PREFIX)
app.include_router(book_copy_router, prefix=API_PREFIX)
app.include_router(bookstore_router, prefix=API_PREFIX)
app.include_router(borrower_router, prefix=API_PREFIX)
app.include_router(loan_router, prefix=API_PREFIX)
app.include_router(fine_router, prefix=API_PREFIX)
app.include_router(notification_router, prefix=API_PREFIX)
app.include_router(library_router, prefix=API_PREFIX)
app.include_router(ebook_router, prefix=API_PREFIX)
app.include_router(ebook_purchase_router, prefix=API_PREFIX)
app.include_router(ocr_router, prefix=API_PREFIX)
app.include_router(reader_router, prefix=API_PREFIX)
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


# ── System health endpoints ──────────────────────────────────────────────────
@app.get("/system/health", tags=["System"])
async def system_health():
    from app.core.database import check_db_connection
    from app.core.redis import check_db_connection as check_redis

    db_ok = await check_db_connection()
    redis_ok = await check_redis()

    return {
        "status": "ok" if db_ok and redis_ok else "degraded",
        "version": settings.APP_VERSION,
        "services": {
            "database": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
        },
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    }


@app.get("/system/readiness", tags=["System"])
async def system_readiness():
    from app.core.database import check_db_connection
    from app.core.redis import check_db_connection as check_redis

    db_ok = await check_db_connection()
    redis_ok = await check_redis()

    if db_ok and redis_ok:
        return {"status": "ready"}
    return {"status": "not ready", "database": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"}


@app.get("/system/liveness", tags=["System"])
async def system_liveness():
    return {"status": "alive"}


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
    }
