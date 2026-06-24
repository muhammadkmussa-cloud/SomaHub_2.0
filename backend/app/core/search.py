"""
Search abstraction layer.
Supports 'basic' (SQL ILIKE fallback) and 'meilisearch' providers.
"""

from typing import Any, List

from app.core.config import settings


async def search_books(
    query: str, tenant_id: str | None = None, limit: int = 20
) -> List[dict[str, Any]] | None:
    """
    Search books. Returns None for 'basic' — callers should apply SQL ILIKE filters.
    For Meilisearch, returns list of matching book dicts.
    """
    provider = settings.SEARCH_PROVIDER
    if provider == "meilisearch":
        return await _meilisearch_search("books", query, limit)
    return None  # Caller handles SQL fallback


async def search_ebooks(query: str, limit: int = 20) -> List[dict[str, Any]] | None:
    """
    Search ebooks. Returns None for 'basic' — callers should apply SQL ILIKE filters.
    """
    provider = settings.SEARCH_PROVIDER
    if provider == "meilisearch":
        return await _meilisearch_search("ebooks", query, limit)
    return None


async def index_book(book_data: dict[str, Any]) -> None:
    """Index a book for search (no-op in basic mode)."""
    if settings.SEARCH_PROVIDER == "meilisearch":
        await _meilisearch_index("books", book_data)


async def index_ebook(ebook_data: dict[str, Any]) -> None:
    """Index an ebook for search (no-op in basic mode)."""
    if settings.SEARCH_PROVIDER == "meilisearch":
        await _meilisearch_index("ebooks", ebook_data)


async def delete_book_index(book_id: str) -> None:
    """Remove a book from the search index."""
    if settings.SEARCH_PROVIDER == "meilisearch":
        await _meilisearch_delete("books", book_id)


async def delete_ebook_index(ebook_id: str) -> None:
    """Remove an ebook from the search index."""
    if settings.SEARCH_PROVIDER == "meilisearch":
        await _meilisearch_delete("ebooks", ebook_id)


# ── Meilisearch ────────────────────────────────────────────────────────


async def _meilisearch_search(
    index_name: str, query: str, limit: int = 20
) -> List[dict[str, Any]]:
    import httpx

    url = f"{settings.MEILISEARCH_URL}/indexes/{index_name}/search"
    headers = {"Content-Type": "application/json"}
    if settings.MEILISEARCH_API_KEY:
        headers["Authorization"] = f"Bearer {settings.MEILISEARCH_API_KEY}"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            headers=headers,
            json={"q": query, "limit": limit},
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("hits", [])


async def _meilisearch_index(index_name: str, document: dict[str, Any]) -> None:
    import httpx

    url = f"{settings.MEILISEARCH_URL}/indexes/{index_name}/documents"
    headers = {"Content-Type": "application/json"}
    if settings.MEILISEARCH_API_KEY:
        headers["Authorization"] = f"Bearer {settings.MEILISEARCH_API_KEY}"

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=[document])
        resp.raise_for_status()


async def _meilisearch_delete(index_name: str, document_id: str) -> None:
    import httpx

    url = f"{settings.MEILISEARCH_URL}/indexes/{index_name}/documents/{document_id}"
    headers = {}
    if settings.MEILISEARCH_API_KEY:
        headers["Authorization"] = f"Bearer {settings.MEILISEARCH_API_KEY}"

    async with httpx.AsyncClient() as client:
        resp = await client.delete(url, headers=headers)
        resp.raise_for_status()
