from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.core.dependencies import CurrentUser, DBSession
from app.core.permissions import UserRole, require_minimum_role
from app.modules.libraries.schemas import LibraryResponse, LibraryUpdate
from app.modules.libraries.service import LibraryService

router = APIRouter(prefix="/libraries", tags=["Libraries"])


@router.get("/profile", response_model=LibraryResponse)
async def get_library_profile(
    current_user: CurrentUser,
    db: DBSession = None,
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant to access library profile."
        )
    service = LibraryService(db)
    return await service.get_profile(UUID(current_user.tenant_id))


@router.put("/profile", response_model=LibraryResponse, dependencies=[Depends(require_minimum_role(UserRole.LIBRARY_ADMIN))])
async def update_library_profile(
    data: LibraryUpdate,
    current_user: CurrentUser,
    db: DBSession = None,
):
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant to update library profile."
        )
    service = LibraryService(db)
    profile = await service.update_profile(UUID(current_user.tenant_id), data)
    await db.commit()
    return profile
