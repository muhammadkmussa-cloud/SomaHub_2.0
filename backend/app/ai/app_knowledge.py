"""
Application knowledge base — indexes SomaHub's navigation, pages, workflows, and help text.
Allows the chatbot to answer "how do I..." questions about using the platform.
"""

import logging
from typing import Any

from app.ai.config import ai_settings
from app.ai.ingestion import IngestionPipeline

logger = logging.getLogger("somahub.ai.app_knowledge")


APP_NAVIGATION = [
    {
        "page": "Landing Page",
        "path": "/",
        "description": "Public marketing page showcasing SomaHub features and pricing.",
        "elements": ["Hero section", "Features grid", "Pricing plans", "CTA buttons", "Footer"],
        "actions": ["Navigate to login", "Navigate to signup", "View features", "View pricing"],
    },
    {
        "page": "Login",
        "path": "/auth/login",
        "description": "User login page for all roles (readers, librarians, admins).",
        "elements": ["Email input", "Password input", "Login button", "Forgot password link"],
        "actions": ["Log in with email and password", "Navigate to forgot password", "Navigate to signup"],
    },
    {
        "page": "Reader Signup",
        "path": "/auth/signup/reader",
        "description": "Registration page for reader accounts to browse and purchase ebooks.",
        "elements": ["Full name input", "Email input", "Password input", "Signup button"],
        "actions": ["Create reader account", "Verify email after signup"],
    },
    {
        "page": "Library Signup",
        "path": "/auth/signup/library",
        "description": "Registration page for new library institutions.",
        "elements": ["Library name input", "Admin email", "Password", "Signup button"],
        "actions": ["Register new library with admin account"],
    },
    {
        "page": "Forgot Password",
        "path": "/auth/forgot-password",
        "description": "Password reset request page.",
        "elements": ["Email input", "Send reset link button"],
        "actions": ["Request password reset email"],
    },
    {
        "page": "Reset Password",
        "path": "/auth/reset-password",
        "description": "Set a new password using a reset token.",
        "elements": ["New password input", "Confirm password", "Reset button"],
        "actions": ["Set new password"],
    },
    {
        "page": "Dashboard",
        "path": "/dashboard",
        "description": "Main dashboard overview showing key metrics: total books, active loans, overdue items, fines due.",
        "elements": ["Summary cards", "Borrowing trends chart", "Recent activity feed"],
        "actions": ["View library statistics", "Monitor overdue items", "Check fine collections"],
    },
    {
        "page": "Books Management",
        "path": "/dashboard/books",
        "description": "Book catalog management for librarians. Add, edit, delete books.",
        "elements": ["Book list table", "Search bar", "Add book button", "Edit and delete actions"],
        "actions": ["Add new book with title, author, ISBN, category", "Edit book details", "Delete books", "Search books by title, author, or ISBN"],
    },
    {
        "page": "Borrowers",
        "path": "/dashboard/borrowers",
        "description": "Manage library patrons/borrowers.",
        "elements": ["Borrower list", "Add borrower button", "Search input", "Suspend borrower option"],
        "actions": ["Register new borrower", "Search borrowers", "Suspend borrower", "View borrower history"],
    },
    {
        "page": "Loans",
        "path": "/dashboard/loans",
        "description": "Book checkout / loan management. Issue and return books.",
        "elements": ["Loans list", "Issue book form", "Return book action", "Mark as lost"],
        "actions": ["Issue book to borrower", "Return borrowed book", "Mark book as lost", "View active loans"],
    },
    {
        "page": "Fines",
        "path": "/dashboard/fines",
        "description": "Fine management for overdue or lost books.",
        "elements": ["Fines list", "Pay fine button", "Waive fine button"],
        "actions": ["Pay fine", "Waive fine", "View outstanding fines"],
    },
    {
        "page": "Bookstore",
        "path": "/dashboard/bookstore",
        "description": "Digital ebook marketplace where readers can browse and purchase ebooks.",
        "elements": ["Ebook grid/list", "Search bar", "Category filter", "Purchase buttons"],
        "actions": ["Browse ebooks", "Search ebooks by title or author", "Filter by category", "Purchase ebook"],
    },
    {
        "page": "My Library",
        "path": "/dashboard/my-library",
        "description": "User's purchased ebooks collection.",
        "elements": ["Book list", "Read button", "Continue reading"],
        "actions": ["View purchased ebooks", "Start reading an ebook", "Continue reading where left off"],
    },
    {
        "page": "Ebook Detail & Reader",
        "path": "/dashboard/bookstore/:ebookId",
        "description": "Ebook detail page with embedded reader, progress tracking, bookmarks, and reviews.",
        "elements": ["Ebook cover", "Title and author info", "Reader view", "Progress bar", "Bookmarks", "Review form"],
        "actions": ["Read ebook", "Bookmark page", "Track reading progress", "Rate and review ebook", "Add to favorites"],
    },
    {
        "page": "Analytics",
        "path": "/dashboard/analytics",
        "description": "Library analytics dashboard for admins.",
        "elements": ["Dashboard stats", "Borrowing trends", "Top books chart"],
        "actions": ["View borrowing trends", "See top books", "Track growth metrics"],
    },
    {
        "page": "Settings",
        "path": "/dashboard/settings",
        "description": "Library profile and user settings.",
        "elements": ["Library name", "Profile form", "Upload logo", "Change password"],
        "actions": ["Update library profile", "Upload library logo", "Change password"],
    },
    {
        "page": "Tenants",
        "path": "/dashboard/tenants",
        "description": "Super admin tenant management page.",
        "elements": ["Tenant list", "Tenant details"],
        "actions": ["View all tenants", "Manage tenant subscriptions"],
    },
    {
        "page": "Admin",
        "path": "/dashboard/admin",
        "description": "Super admin platform administration panel.",
        "elements": ["Platform stats", "System configuration"],
        "actions": ["Manage platform settings", "View global statistics"],
    },
]


APP_WORKFLOWS = [
    {
        "name": "Borrow a book (librarian workflow)",
        "steps": [
            "1. Go to /dashboard/loans",
            "2. Click 'Issue Book' or 'New Loan'",
            "3. Select the borrower from the list or search by name",
            "4. Select the book copy to issue",
            "5. Set the due date (if applicable)",
            "6. Confirm to create the loan",
        ],
        "notes": "Only librarians and library admins can issue loans. The book must have available copies.",
    },
    {
        "name": "Return a book (librarian workflow)",
        "steps": [
            "1. Go to /dashboard/loans",
            "2. Find the active loan in the list",
            "3. Click 'Return Book'",
            "4. System updates availability and calculates any fines for overdue items",
        ],
        "notes": "Returns increase the available copies count. Overdue items automatically generate fines.",
    },
    {
        "name": "Reserve a book (reader workflow)",
        "steps": [
            "1. Browse the catalog on /dashboard/books",
            "2. Find the book you want",
            "3. Check if copies are available",
            "4. Contact library staff to place a hold (currently managed by librarians)",
        ],
        "notes": "Reservation features may be expanded in future updates.",
    },
    {
        "name": "Renew a borrowed book",
        "steps": [
            "1. Request renewal from the librarian",
            "2. Librarian can update the due date on the existing loan in /dashboard/loans",
            "3. The loan's due date is extended",
        ],
        "notes": "Renewals are subject to library policy. Some items may not be renewable.",
    },
    {
        "name": "Search for books",
        "steps": [
            "1. Go to /dashboard/books",
            "2. Use the search bar to search by title, author, or ISBN",
            "3. Results update in real-time as you type",
            "4. Click on a book to view details",
        ],
        "notes": "The search uses ILIKE matching on title, author, and ISBN.",
    },
    {
        "name": "Purchase an ebook",
        "steps": [
            "1. Go to /dashboard/bookstore",
            "2. Browse or search for ebooks",
            "3. Click on an ebook to see details",
            "4. Click 'Buy' or 'Checkout' to purchase",
            "5. After purchase, the ebook appears in /dashboard/my-library",
        ],
        "notes": "Free ebooks can be checked out without payment. Paid ebooks require Stripe or Paystack payment.",
    },
    {
        "name": "Read an ebook",
        "steps": [
            "1. Go to /dashboard/my-library",
            "2. Click 'Read' on any ebook you own",
            "3. The ebook reader opens with your last saved position",
            "4. Use bookmarks to save pages",
            "5. Reading progress is saved automatically",
        ],
        "notes": "Progress syncs across sessions. You can rate and review books after reading.",
    },
    {
        "name": "Change password",
        "steps": [
            "1. Go to /dashboard/settings",
            "2. Find the password change section",
            "3. Enter current password",
            "4. Enter new password",
            "5. Confirm new password",
            "6. Submit to save changes",
        ],
        "notes": "Password changes require your current password for security.",
    },
    {
        "name": "Upload profile picture",
        "steps": [
            "1. Go to /dashboard/settings",
            "2. Click on the avatar/profile picture area",
            "3. Select an image file to upload",
            "4. Save your changes",
        ],
        "notes": "Profile pictures are stored in the configured storage backend (local, S3, or Supabase).",
    },
    {
        "name": "Add a new book to catalog",
        "steps": [
            "1. Go to /dashboard/books",
            "2. Click 'Add Book' or 'New Book'",
            "3. Fill in: Title (required), Author (required), ISBN, Publisher, Category, Publication Year",
            "4. Set the total number of copies",
            "5. Optionally upload a cover image",
            "6. Submit to create the book record",
            "7. Add individual copies with barcodes via the copies section",
        ],
        "notes": "Only librarians and library admins can add books. The ISBN must be unique per tenant.",
    },
    {
        "name": "Upload an ebook",
        "steps": [
            "1. Go to /dashboard/books or bookstore section",
            "2. Use the ebook upload form",
            "3. Select the ebook file",
            "4. Fill in metadata: title, author, description, category, price",
            "5. Set to 'published' to make it available in the bookstore",
        ],
        "notes": "Ebooks can be free or priced. Supported formats depend on the reader implementation.",
    },
]


APP_FAQS = [
    {
        "question": "How do I borrow a book?",
        "answer": "Borrowing is managed by librarians. Go to /dashboard/loans, click 'Issue Book', select the borrower and book copy, set a due date, and confirm the loan.",
    },
    {
        "question": "How do I return a book?",
        "answer": "Go to /dashboard/loans, find the active loan, and click 'Return Book'. The system will update availability and calculate any overdue fines.",
    },
    {
        "question": "How do I search for books?",
        "answer": "Use the search bar on /dashboard/books. You can search by title, author, or ISBN. Results update as you type.",
    },
    {
        "question": "How do I change my password?",
        "answer": "Go to /dashboard/settings, find the password section, enter your current and new password, then save.",
    },
    {
        "question": "How do I purchase an ebook?",
        "answer": "Browse ebooks in /dashboard/bookstore, click on one you like, then click 'Buy' or 'Checkout'. Free ebooks are available immediately.",
    },
    {
        "question": "Where do I find my purchased ebooks?",
        "answer": "Your purchased ebooks are in /dashboard/my-library. Click 'Read' to start reading.",
    },
    {
        "question": "How do I upload a profile picture?",
        "answer": "Go to /dashboard/settings, click on the avatar area, select an image, and save.",
    },
    {
        "question": "How do I view my reading progress?",
        "answer": "Open any ebook from /dashboard/my-library. Your progress is saved and displayed automatically in the reader view.",
    },
    {
        "question": "How do I add a bookmark?",
        "answer": "While reading an ebook, use the bookmark button to save your current page. View all bookmarks in the bookmarks section.",
    },
    {
        "question": "How do I rate a book?",
        "answer": "After reading an ebook, you can rate it 1-5 stars and leave a review on the ebook detail page.",
    },
    {
        "question": "How do I view library analytics?",
        "answer": "Library admins can access /dashboard/analytics to view borrowing trends, top books, and growth metrics.",
    },
    {
        "question": "How do I manage fines?",
        "answer": "Go to /dashboard/fines. You can view outstanding fines, process payments, or waive fines for borrowers.",
    },
    {
        "question": "How do I suspend a borrower?",
        "answer": "Go to /dashboard/borrowers, find the borrower, and use the 'Suspend' option. Suspended borrowers cannot check out books.",
    },
    {
        "question": "How do I add a new borrower?",
        "answer": "Go to /dashboard/borrowers and click 'Add Borrower'. Fill in their details and submit.",
    },
    {
        "question": "Why can't I see certain pages?",
        "answer": "Page access is based on your role. Readers can see bookstore and my-library. Librarians see books, borrowers, loans, fines. Admins see analytics and settings. If you can't see a page, you may not have the required permissions.",
    },
]


class AppKnowledgeBase:
    def __init__(self, ingestion_pipeline: IngestionPipeline | None = None):
        self.ingestion = ingestion_pipeline or IngestionPipeline()
        self._indexed = False

    async def index_all(self) -> int:
        total = 0
        total += await self._index_navigation()
        total += await self._index_workflows()
        total += await self._index_faqs()
        self._indexed = True
        logger.info("App knowledge base indexed: %d total entries", total)
        return total

    async def _index_navigation(self) -> int:
        count = 0
        for page in APP_NAVIGATION:
            text = f"Page: {page['page']}\nPath: {page['path']}\nDescription: {page['description']}\n"
            text += f"Elements: {', '.join(page['elements'])}\n"
            text += f"Actions: {', '.join(page['actions'])}"

            count += await self.ingestion.ingest_text(
                text=text,
                source_id=f"app_nav:{page['path']}",
                source_type="app_navigation",
                extra_metadata={
                    "category": "navigation",
                    "page": page["page"],
                    "path": page["path"],
                },
            )
        return count

    async def _index_workflows(self) -> int:
        count = 0
        for workflow in APP_WORKFLOWS:
            text = f"Workflow: {workflow['name']}\n\nSteps:\n"
            text += "\n".join(workflow["steps"])
            text += f"\n\nNotes: {workflow['notes']}"

            count += await self.ingestion.ingest_text(
                text=text,
                source_id=f"app_workflow:{workflow['name']}",
                source_type="app_workflow",
                extra_metadata={
                    "category": "workflow",
                    "workflow_name": workflow["name"],
                },
            )
        return count

    async def _index_faqs(self) -> int:
        count = 0
        for faq in APP_FAQS:
            text = f"Q: {faq['question']}\nA: {faq['answer']}"

            count += await self.ingestion.ingest_text(
                text=text,
                source_id=f"app_faq:{faq['question']}",
                source_type="app_faq",
                extra_metadata={
                    "category": "faq",
                    "question": faq["question"],
                },
            )
        return count

    @property
    def is_indexed(self) -> bool:
        return self._indexed
