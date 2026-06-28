from pydantic import BaseModel


class OCRStudentIDResponse(BaseModel):
    name: str | None = None
    student_id: str | None = None


class OCRISBNResponse(BaseModel):
    isbn: str | None = None
    title: str | None = None
    author: str | None = None


class OCRBookCoverResponse(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    authors: list[str] = []
    publisher: str | None = None
    isbn: str | None = None
    publication_year: int | None = None
    edition: str | None = None
    language: str | None = None
    categories: list[str] = []
    description: str | None = None
    subjects: list[str] = []
