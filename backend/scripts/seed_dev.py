#!/usr/bin/env python3
"""
Seed script for local development.
Creates a superadmin user and optionally a demo tenant with staff/readers.
Usage:
    uv run python scripts/seed_dev.py
    uv run python scripts/seed_dev.py --with-demo
"""

import argparse
import asyncio
import os
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("APP_ENV", "development")

from app.core.database import Base
from app.core.security import hash_password
from app.modules.auth.models import Tenant, User


DEV_SUPERADMIN_EMAIL = "admin@somahub.io"
DEV_SUPERADMIN_PASSWORD = "Admin123!"
DEV_SUPERADMIN_USERNAME = "superadmin"


async def seed(with_demo: bool = False) -> None:
    from app.core.config import settings

    database_url = settings.DATABASE_URL
    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        # ── Create Super Admin ──────────────────────────────────────────
        from app.modules.auth.repository import UserRepository
        user_repo = UserRepository(session)
        existing = await user_repo.get_by_email(DEV_SUPERADMIN_EMAIL)
        if existing:
            print(f"Superadmin already exists: {DEV_SUPERADMIN_EMAIL}")
        else:
            user = User(
                id=uuid4(),
                tenant_id=None,
                email=DEV_SUPERADMIN_EMAIL,
                username=DEV_SUPERADMIN_USERNAME,
                hashed_password=hash_password(DEV_SUPERADMIN_PASSWORD),
                role="super_admin",
                is_active=True,
                is_email_verified=True,
            )
            session.add(user)
            await session.flush()
            print(f"Created superadmin: {DEV_SUPERADMIN_EMAIL} / {DEV_SUPERADMIN_PASSWORD}")

        # ── Optional Demo Tenant ───────────────────────────────────────
        if with_demo:
            from app.modules.tenants.repository import TenantRepository
            tenant_repo = TenantRepository(session)
            demo_tenant = await tenant_repo.get_by_slug("demo-library")
            if demo_tenant:
                print("Demo tenant already exists.")
            else:
                tenant = Tenant(
                    id=uuid4(),
                    name="Demo Library",
                    slug="demo-library",
                    email="demo@library.com",
                    library_type="public",
                    location="Demo City",
                    is_active=True,
                    plan="professional",
                )
                session.add(tenant)
                await session.flush()

                librarian = User(
                    id=uuid4(),
                    tenant_id=tenant.id,
                    email="librarian@demo.com",
                    username="demolibrarian",
                    hashed_password=hash_password("Library123!"),
                    role="librarian",
                    is_active=True,
                    is_email_verified=True,
                )
                session.add(librarian)

                admin = User(
                    id=uuid4(),
                    tenant_id=tenant.id,
                    email="library@demo.com",
                    username="demoadmin",
                    hashed_password=hash_password("Library123!"),
                    role="library_admin",
                    is_active=True,
                    is_email_verified=True,
                )
                session.add(admin)

                reader = User(
                    id=uuid4(),
                    tenant_id=tenant.id,
                    email="reader@demo.com",
                    username="demoreader",
                    hashed_password=hash_password("Reader123!"),
                    role="reader",
                    is_active=True,
                    is_email_verified=True,
                )
                session.add(reader)

                print("Created demo tenant with librarian, admin, and reader users.")

        await session.commit()
        print("\n✅ Development seed complete!")

    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed dev database")
    parser.add_argument("--with-demo", action="store_true", help="Also create demo tenant")
    args = parser.parse_args()
    asyncio.run(seed(with_demo=args.with_demo))
