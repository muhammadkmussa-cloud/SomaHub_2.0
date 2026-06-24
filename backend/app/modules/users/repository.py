from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import User


class UserCRUDRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, user_id: UUID, tenant_id: UUID | None = None
    ) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        if tenant_id is not None:
            stmt = stmt.where(User.tenant_id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tenant_id(
        self, tenant_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[User]:
        result = await self.session.execute(
            select(User)
            .where(User.tenant_id == tenant_id)
            .offset(offset)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_all(
        self, limit: int = 100, offset: int = 0, tenant_id: UUID | None = None
    ) -> List[User]:
        stmt = select(User)
        if tenant_id is not None:
            stmt = stmt.where(User.tenant_id == tenant_id)
        stmt = stmt.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
