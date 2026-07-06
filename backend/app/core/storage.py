"""
File storage abstraction layer.
Supports 'local', 'supabase', and 's3' storage backends.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def upload_file(file: UploadFile, folder: str = "general") -> str:
    """Upload a file and return its URL. Delegates to the configured provider."""
    ext = ""
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

    provider = settings.STORAGE_PROVIDER

    if provider == "s3":
        return await _upload_s3(file, folder, filename)
    elif provider == "supabase":
        return await _upload_supabase(file, folder, filename)
    else:
        return await _upload_local(file, folder, filename)


async def upload_bytes(content: bytes, filename: str, folder: str = "general") -> str:
    """Upload raw bytes and return the URL. Delegates to the configured provider."""
    provider = settings.STORAGE_PROVIDER

    if provider == "s3":
        import boto3
        bucket = _s3_bucket_for(folder)
        key = f"{folder}/{filename}"
        session = boto3.Session(
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        client = session.client("s3", endpoint_url=settings.S3_ENDPOINT or None)
        client.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            ContentType="image/png" if filename.endswith(".png") else "application/octet-stream",
        )
        if settings.S3_ENDPOINT:
            return f"{settings.S3_ENDPOINT}/{bucket}/{key}"
        return f"https://{bucket}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
    elif provider == "supabase":
        import httpx
        bucket = _supabase_bucket_for(folder)
        url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                    "Content-Type": "image/png" if filename.endswith(".png") else "application/octet-stream",
                },
                content=content,
            )
            resp.raise_for_status()
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"
    else:
        dir_path = UPLOAD_DIR / folder
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path = dir_path / filename
        file_path.write_bytes(content)
        return f"/uploads/{folder}/{filename}"


async def delete_file(url: str) -> None:
    """Delete a file by its URL. Delegates to the configured provider."""
    provider = settings.STORAGE_PROVIDER

    if provider == "s3":
        await _delete_s3(url)
    elif provider == "supabase":
        await _delete_supabase(url)
    else:
        await _delete_local(url)


# ── Local ──────────────────────────────────────────────────────────────


async def _upload_local(file: UploadFile, folder: str, filename: str) -> str:
    dir_path = UPLOAD_DIR / folder
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename

    content = await file.read()
    file_path.write_bytes(content)

    return f"/uploads/{folder}/{filename}"


async def _delete_local(url: str) -> None:
    # url is like /uploads/folder/filename
    relative = url.lstrip("/")
    file_path = Path(relative)
    if file_path.exists():
        file_path.unlink()


# ── S3 ─────────────────────────────────────────────────────────────────


async def _upload_s3(file: UploadFile, folder: str, filename: str) -> str:
    import boto3

    bucket = _s3_bucket_for(folder)
    key = f"{folder}/{filename}"

    session = boto3.Session(
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )
    client = session.client("s3", endpoint_url=settings.S3_ENDPOINT or None)

    content = await file.read()
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=content,
        ContentType=file.content_type or "application/octet-stream",
    )

    if settings.S3_ENDPOINT:
        return f"{settings.S3_ENDPOINT}/{bucket}/{key}"
    return f"https://{bucket}.s3.{settings.S3_REGION}.amazonaws.com/{key}"


async def _delete_s3(url: str) -> None:
    import boto3

    session = boto3.Session(
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )
    client = session.client("s3", endpoint_url=settings.S3_ENDPOINT or None)

    # Extract bucket and key from URL
    parts = url.split("/")
    bucket = parts[3] if len(parts) > 3 else ""
    key = "/".join(parts[4:]) if len(parts) > 4 else ""

    if bucket and key:
        client.delete_object(Bucket=bucket, Key=key)


# ── Supabase ────────────────────────────────────────────────────────────


async def _upload_supabase(file: UploadFile, folder: str, filename: str) -> str:
    import httpx

    bucket = _supabase_bucket_for(folder)
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{filename}"

    content = await file.read()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                "Content-Type": file.content_type or "application/octet-stream",
            },
            content=content,
        )
        resp.raise_for_status()

    return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{filename}"


async def _delete_supabase(url: str) -> None:
    import httpx

    # url: https://<project>.supabase.co/storage/v1/object/public/<bucket>/<key>
    bucket, key = "", ""
    parts = url.split("/public/")
    if len(parts) == 2:
        bucket_key = parts[1]
        if "/" in bucket_key:
            bucket = bucket_key.split("/")[0]
            key = "/".join(bucket_key.split("/")[1:])

    if not bucket or not key:
        return

    delete_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{key}"
    async with httpx.AsyncClient() as client:
        await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"},
        )


# ── Helpers ──────────────────────────────────────────────────────────────


def _s3_bucket_for(folder: str) -> str:
    mapping = {
        "ebooks": settings.S3_BUCKET_EBOOKS,
        "covers": settings.S3_BUCKET_COVERS,
        "avatars": settings.S3_BUCKET_AVATARS,
        "ocr-uploads": "somahub-ocr-uploads",
    }
    return mapping.get(folder, "somahub-uploads")


def _supabase_bucket_for(folder: str) -> str:
    mapping = {
        "ebooks": settings.SUPABASE_BUCKET_EBOOKS,
        "covers": settings.SUPABASE_BUCKET_COVERS,
        "avatars": settings.SUPABASE_BUCKET_AVATARS,
        "ocr-uploads": settings.SUPABASE_BUCKET_OCR,
    }
    return mapping.get(folder, "uploads")
