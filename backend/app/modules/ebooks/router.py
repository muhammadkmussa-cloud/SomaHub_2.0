import logging
import asyncio
from pathlib import Path
from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, File, UploadFile

from app.core.storage import upload_file, UPLOAD_DIR

from app.core.dependencies import CurrentUser, DBSession, OptionalUser
from app.core.permissions import UserRole, has_minimum_role, require_role
from app.modules.ebooks.schemas import EbookCreate, EbookResponse, EbookUpdate
from app.modules.ebooks.service import EbookService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ebooks", tags=["Ebooks"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _local_path_from_url(file_url: str) -> Path | None:
    """
    Convert a stored URL like /uploads/ebooks/abc.pdf to the local filesystem path.
    Works when STORAGE_PROVIDER == 'local'.
    """
    if not file_url:
        return None
    # strip leading slash
    relative = file_url.lstrip("/")
    path = Path(relative)  # relative to CWD (backend/)
    return path if path.exists() else None


async def _extract_and_store_content(ebook_id: UUID, file_url: str, db) -> None:
    """
    Background task: extract structured text from the PDF and persist to ebook.content.
    Runs in a thread-pool executor so PyMuPDF (synchronous) doesn't block the event loop.
    """
    from app.core.pdf_processor import extract_structured_text

    path = _local_path_from_url(file_url)
    if not path:
        logger.warning("PDF not found for extraction: %s", file_url)
        return

    service = EbookService(db)
    try:
        ebook = await service.get_ebook(ebook_id)
    except Exception as exc:
        logger.error("Failed to retrieve ebook %s for extraction: %s", ebook_id, exc)
        return

    logger.info("Extracting PDF content for ebook %s …", ebook_id)

    # Run synchronous PyMuPDF in a thread so we don't block the event loop
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(
        None,
        extract_structured_text,
        path,
        ebook.title,
        ebook.author
    )

    if not content:
        logger.warning("No extractable text found in PDF: %s", file_url)
        return

    try:
        await service.update_ebook(ebook_id, EbookUpdate(content=content))
        await db.commit()
        logger.info(
            "Content stored for ebook %s (%d chars)", ebook_id, len(content)
        )
    except Exception as exc:
        logger.error("Failed to store extracted content: %s", exc)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[EbookResponse])
async def list_ebooks(
    search: str | None = None,
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
    current_user: OptionalUser = None,
    db: DBSession = None,
):
    service = EbookService(db)

    # Readers see only published ebooks. Librarians/Admins can see all
    status_filter = "published"
    if current_user and has_minimum_role(current_user.role, UserRole.LIBRARIAN):
        status_filter = None  # Show all statuses (draft, published, archived)

    return await service.list_ebooks(
        search=search,
        category=category,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )


@router.get("/{ebook_id}", response_model=EbookResponse)
async def get_ebook(
    ebook_id: UUID,
    db: DBSession = None,
):
    service = EbookService(db)
    return await service.get_ebook(ebook_id)


@router.post(
    "",
    response_model=EbookResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def create_ebook(
    data: EbookCreate,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: DBSession = None,
):
    service = EbookService(db)
    tenant_id = UUID(current_user.tenant_id) if current_user.tenant_id else None
    ebook = await service.create_ebook(tenant_id, data)
    await db.commit()
    await db.refresh(ebook)

    # If a PDF was attached, kick off extraction in the background
    if ebook.file_url and ebook.file_url.lower().endswith(".pdf"):
        background_tasks.add_task(
            _extract_and_store_content, ebook.id, ebook.file_url, db
        )

    return ebook


@router.put(
    "/{ebook_id}",
    response_model=EbookResponse,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def update_ebook(
    ebook_id: UUID,
    data: EbookUpdate,
    background_tasks: BackgroundTasks,
    db: DBSession = None,
):
    service = EbookService(db)
    ebook = await service.update_ebook(ebook_id, data)
    await db.commit()
    await db.refresh(ebook)

    # Re-extract if file_url changed to a new PDF
    if data.file_url and data.file_url.lower().endswith(".pdf"):
        background_tasks.add_task(
            _extract_and_store_content, ebook_id, data.file_url, db
        )

    return ebook


@router.delete(
    "/{ebook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def delete_ebook(
    ebook_id: UUID,
    db: DBSession = None,
):
    service = EbookService(db)
    await service.delete_ebook(ebook_id)
    await db.commit()


# ── File upload endpoints ─────────────────────────────────────────────────────

@router.post(
    "/upload-file",
    response_model=dict,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def upload_ebook_file(
    file: UploadFile = File(...),
):
    """Upload a PDF and return its URL. Content extraction happens when the ebook record is created/updated."""
    if file.content_type and file.content_type not in (
        "application/pdf",
        "application/octet-stream",
    ):
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are accepted for ebook uploads.",
            )
    url = await upload_file(file, folder="ebooks")
    return {"url": url}


@router.post(
    "/upload-cover",
    response_model=dict,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
)
async def upload_ebook_cover(
    file: UploadFile = File(...),
):
    url = await upload_file(file, folder="covers")
    return {"url": url}


# ── Re-process endpoint (admin utility) ──────────────────────────────────────

@router.post(
    "/{ebook_id}/process-pdf",
    response_model=EbookResponse,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))],
    summary="Re-extract PDF content",
)
async def reprocess_pdf(
    ebook_id: UUID,
    background_tasks: BackgroundTasks,
    db: DBSession = None,
):
    """
    Trigger PDF text extraction for an existing ebook.
    Useful when a PDF was uploaded before extraction was implemented,
    or when you want to refresh the content after replacing the file.
    """
    service = EbookService(db)
    ebook = await service.get_ebook(ebook_id)

    if not ebook.file_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This ebook has no uploaded PDF file.",
        )
    if not ebook.file_url.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Linked file is not a PDF.",
        )

    path = _local_path_from_url(ebook.file_url)
    if not path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF file not found on disk: {ebook.file_url}",
        )

    background_tasks.add_task(
        _extract_and_store_content, ebook_id, ebook.file_url, db
    )

    return ebook
