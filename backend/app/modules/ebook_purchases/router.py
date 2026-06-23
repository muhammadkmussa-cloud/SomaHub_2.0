from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DBSession
from app.modules.ebook_purchases.schemas import EbookPurchaseCreate, EbookPurchaseResponse
from app.modules.ebook_purchases.service import EbookPurchaseService
from app.modules.ebooks.service import EbookService

router = APIRouter(prefix="/ebook-purchases", tags=["Ebook Purchases"])


@router.get("/my-library", response_model=List[EbookPurchaseResponse])
async def get_my_library(
    current_user: CurrentUser,
    limit: int = 100,
    offset: int = 0,
    db: DBSession = None,
):
    service = EbookPurchaseService(db)
    return await service.list_user_purchases(UUID(current_user.user_id), limit, offset)


@router.get("/check/{ebook_id}")
async def check_ownership(
    ebook_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = EbookPurchaseService(db)
    owned = await service.check_ownership(UUID(current_user.user_id), ebook_id)
    return {"ebook_id": ebook_id, "owned": owned}


@router.post("/checkout-free", response_model=EbookPurchaseResponse)
async def checkout_free_ebook(
    ebook_id: UUID,
    current_user: CurrentUser,
    db: DBSession = None,
):
    ebook_service = EbookService(db)
    ebook = await ebook_service.get_ebook(ebook_id)
    
    if ebook.price > 0.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout priced ebook using checkout-free endpoint."
        )

    purchase_service = EbookPurchaseService(db)
    purchase_data = EbookPurchaseCreate(
        ebook_id=ebook_id,
        amount=0.00,
        currency="USD",
    )
    purchase = await purchase_service.register_purchase(UUID(current_user.user_id), purchase_data)
    await db.commit()
    return purchase
