from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.redis import get_short_token

router = APIRouter(prefix="/internal/debug", tags=["Debug"])


@router.get("/verify-token/{user_id}")
async def get_verify_token(user_id: str):
    """Return the verification short token for a user (development only)."""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    token = await get_short_token("verify", user_id)
    return {"token": token}
