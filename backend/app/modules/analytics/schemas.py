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
