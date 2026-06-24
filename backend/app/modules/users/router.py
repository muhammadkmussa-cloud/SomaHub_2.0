from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import DBSession, CurrentUser
from app.core.permissions import UserRole, require_minimum_role
from app.modules.users.schemas import UserProfileUpdate, UserResponse, UserRoleUpdate
from app.modules.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: CurrentUser, db: DBSession = None):
    """Retrieve the profile of the currently logged-in user."""
    service = UserService(db)
    return await service.get_user(UUID(current_user.user_id))


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserProfileUpdate, current_user: CurrentUser, db: DBSession = None
):
    """Update the profile of the currently logged-in user."""
    service = UserService(db)
    user = await service.update_profile(UUID(current_user.user_id), data)
    await db.commit()
    return user


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: CurrentUser, limit: int = 100, offset: int = 0, db: DBSession = None
):
    """
    List users (Librarians/Library Admins can view tenant users, Super Admin views all).
    """
    service = UserService(db)

    if current_user.role == UserRole.SUPER_ADMIN.value:
        return await service.list_users(limit=limit, offset=offset)

    # Non-super admin must belong to a tenant and can only see users of that tenant
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to view users.",
        )

    # Restrict to library admin or librarian
    if current_user.role not in [
        UserRole.LIBRARY_ADMIN.value,
        UserRole.LIBRARIAN.value,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to list users.",
        )

    return await service.list_users(
        tenant_id=UUID(current_user.tenant_id), limit=limit, offset=offset
    )


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))],
)
async def update_user_role(
    user_id: UUID, data: UserRoleUpdate, current_user: CurrentUser, db: DBSession = None
):
    """Update the role of a user (Library Admin or Super Admin only)."""
    service = UserService(db)
    user = await service.get_user(user_id)

    # If not super admin, check that the user belongs to the same tenant
    if current_user.role != UserRole.SUPER_ADMIN.value:
        if not current_user.tenant_id or user.tenant_id != UUID(current_user.tenant_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage users belonging to your library.",
            )

        # Library admins cannot promote someone to super admin
        if data.role == UserRole.SUPER_ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot assign the super admin role.",
            )

    updated_user = await service.update_role(user_id, data)
    await db.commit()
    return updated_user
