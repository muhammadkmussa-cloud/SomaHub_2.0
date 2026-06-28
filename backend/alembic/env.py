"""
Alembic environment configuration for async SQLAlchemy.
"""

import asyncio
from logging.config import fileConfig
import sys
import os

# Add backend root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.core.database import Base

# Import all models so Alembic can detect them
from app.modules.audit.models import AuditLog  # noqa: F401
from app.modules.auth.models import User, Tenant  # noqa: F401
from app.modules.books.models import Book, BookCopy  # noqa: F401
from app.modules.borrowers.models import Borrower  # noqa: F401
from app.modules.fines.models import Fine  # noqa: F401
from app.modules.loans.models import Loan  # noqa: F401
from app.modules.libraries.models import Library  # noqa: F401
from app.modules.ebooks.models import Ebook  # noqa: F401
from app.modules.payments.models import Payment  # noqa: F401
from app.modules.ebook_purchases.models import EbookPurchase  # noqa: F401
from app.modules.reading_progress.models import ReadingProgress  # noqa: F401
from app.modules.bookmarks.models import Bookmark  # noqa: F401
from app.modules.favorites.models import Favorite  # noqa: F401
from app.modules.reviews.models import Review  # noqa: F401
from app.modules.subscriptions.models import Subscription  # noqa: F401

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url with our settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ── Offline mode ──────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (async) ───────────────────────────────────────────────────────
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
