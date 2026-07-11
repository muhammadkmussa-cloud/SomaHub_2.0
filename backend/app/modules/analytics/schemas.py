from typing import List

from pydantic import BaseModel


class BookStat(BaseModel):
    book_id: str
    title: str
    author: str
    borrow_count: int


class TrendPoint(BaseModel):
    date: str
    count: int


class DashboardAnalytics(BaseModel):
    total_books: int = 0
    total_borrowers: int = 0
    active_loans: int = 0
    overdue_loans: int = 0
    total_fines_collected: float = 0.0
    total_ebook_sales: int = 0
    revenue_this_month: float = 0.0
    top_books: List[BookStat] = []


class TrendResponse(BaseModel):
    trends: List[TrendPoint] = []


class TopBooksResponse(BaseModel):
    books: List[BookStat] = []


# --- Platform Cockpit Analytics for Super Admin ---
from datetime import datetime

class PlatformKPIs(BaseModel):
    total_tenants: int = 0
    active_tenants_this_week: int = 0
    total_ecosystem_users: int = 0
    total_catalog_books: int = 0
    total_ebook_sales: int = 0
    mrr: float = 0.0


class TenantStorageStat(BaseModel):
    tenant_id: str
    tenant_name: str
    upload_count: int
    estimated_mb: float


class StorageStats(BaseModel):
    total_uploads: int = 0
    estimated_total_mb: float = 0.0
    top_tenants: List[TenantStorageStat] = []


class TenantLeaderboardEntry(BaseModel):
    tenant_id: str
    name: str
    slug: str
    plan: str
    loan_count_7d: int = 0
    total_borrowers: int = 0
    is_active: bool
    created_at: datetime


class TenantLeaderboardResponse(BaseModel):
    top_tenants: List[TenantLeaderboardEntry] = []
    recent_signups: List[TenantLeaderboardEntry] = []

