import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.ai.ocr import OCRPipeline
from app.core.dependencies import CurrentUser
from app.core.permissions import UserRole, require_role
from app.modules.ocr.schemas import (
    OCRBookCoverResponse,
    OCRISBNResponse,
    OCRStudentIDResponse,
)

logger = logging.getLogger("somahub.ocr")

router = APIRouter(
    prefix="/ocr",
    tags=["OCR"],
    dependencies=[Depends(require_role(UserRole.LIBRARY_ADMIN, UserRole.LIBRARIAN, UserRole.SUPER_ADMIN))],
)


def get_ocr_pipeline() -> OCRPipeline:
    return OCRPipeline()


@router.post("/student-id", response_model=OCRStudentIDResponse)
async def scan_student_id(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    ocr: OCRPipeline = Depends(get_ocr_pipeline),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    try:
        metadata = await ocr.process_book_image(content)
        return OCRStudentIDResponse(
            name=metadata.get("title"),
            student_id=metadata.get("isbn"),
        )
    except Exception as e:
        logger.error("Student ID scan failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")


@router.post("/isbn", response_model=OCRISBNResponse)
async def scan_isbn(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    ocr: OCRPipeline = Depends(get_ocr_pipeline),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    try:
        metadata = await ocr.process_book_image(content)
        return OCRISBNResponse(
            isbn=metadata.get("isbn"),
            title=metadata.get("title"),
            author=", ".join(metadata.get("authors", [])),
        )
    except Exception as e:
        logger.error("ISBN scan failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")


@router.post("/book-cover", response_model=OCRBookCoverResponse)
async def scan_book_cover(
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
    ocr: OCRPipeline = Depends(get_ocr_pipeline),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    content = await file.read()
    try:
        metadata = await ocr.process_book_image(content)
        return OCRBookCoverResponse(**metadata)
    except Exception as e:
        logger.error("Book cover scan failed: %s", e)
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")
