from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import User
from app.modules.users.repository import UserCRUDRepository
from app.modules.users.schemas import UserProfileUpdate, UserRoleUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserCRUDRepository(session)

    async def get_user(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def list_users(
        self, tenant_id: Optional[UUID] = None, limit: int = 100, offset: int = 0
    ) -> List[User]:
        if tenant_id:
            return await self.repo.get_by_tenant_id(tenant_id, limit, offset)
        return await self.repo.get_all(limit, offset)

    async def update_profile(self, user_id: UUID, data: UserProfileUpdate) -> User:
        user = await self.get_user(user_id)
        return await self.repo.update(user, **data.model_dump(exclude_unset=True))

    async def update_role(self, user_id: UUID, data: UserRoleUpdate) -> User:
        user = await self.get_user(user_id)
        # Prevent demoting the last super admin or self-modification if we want,
        # but let's keep it simple for now.
        return await self.repo.update(user, role=data.role)

    async def change_password(self, user_id: UUID, current_password: str, new_password: str, session_id: str = None) -> None:
        user = await self.get_user(user_id)
        from app.core.security import verify_password, hash_password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        hashed = hash_password(new_password)
        await self.repo.update(user, hashed_password=hashed)
        
        from app.core.redis import revoke_all_sessions
        await revoke_all_sessions(str(user_id), except_session_id=session_id)

    async def update_preferences(
        self, user_id: UUID, timezone: Optional[str] = None, theme: Optional[str] = None, notification_prefs: Optional[dict] = None
    ) -> User:
        user = await self.get_user(user_id)
        updates = {}
        if timezone is not None:
            updates["timezone"] = timezone
        if theme is not None:
            updates["theme"] = theme
        if notification_prefs is not None:
            # Merge with existing if needed, or replace. Let's merge or replace depending on what we want.
            # Usually replacing the whole pref payload is fine, but merging is safer. Let's merge!
            existing = user.notification_prefs or {}
            updates["notification_prefs"] = {**existing, **notification_prefs}
            
        return await self.repo.update(user, **updates)
