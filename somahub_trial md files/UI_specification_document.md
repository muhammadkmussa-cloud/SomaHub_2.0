# SomaHub Enterprise

# UI Specification Document (USD)

Version: 1.0

---

# 1. Design Philosophy

SomaHub should feel:

* Modern
* Professional
* Fast
* Clean
* Reading-focused
* Dashboard-driven

The interface should avoid clutter and prioritize usability over visual effects.

---

# 2. Design Principles

## Consistency

All pages must follow the same:

* spacing system
* typography scale
* button styles
* form styles
* navigation structure

---

## Mobile First

Every screen must work on:

* Mobile
* Tablet
* Desktop

---

## Accessibility

Minimum requirements:

* Keyboard navigation
* Visible focus states
* Proper color contrast
* Screen reader support

---

# 3. Design System

## Colors

### Primary

Royal Emerald

Used for:

* Primary buttons
* Active states
* Success indicators

---

### Secondary

Sapphire Blue

Used for:

* Links
* Charts
* Information cards

---

### Neutral

Obsidian Black

Used for:

* Text
* Navigation
* Headers

---

### Background

Arctic White

Used for:

* Page backgrounds
* Cards

---

## Status Colors

Success

* Green

Warning

* Amber

Error

* Red

Information

* Blue

---

# 4. Typography

## Headings

Font:

Satoshi

Weights:

* 600
* 700

---

## Body

Font:

Inter

Weights:

* 400
* 500

---

## UI Labels

Font:

Geist

Weights:

* 500

---

# 5. Layout System

Desktop:

```text
Sidebar
+
Top Navbar
+
Content Area
```

---

Mobile:

```text
Top Navigation
+
Drawer Menu
+
Content Area
```

---

# 6. Landing Page

## Hero Section

Headline:

Library Management Reimagined

Subheadline:

Manage books, borrowers, payments, digital reading, and analytics from one platform.

---

CTA Buttons

Primary:

Start Free

Secondary:

Book Demo

Tertiary:

Browse Books

---

## Hero Visual

Animated dashboard preview showing:

* active borrowers
* books issued
* overdue books
* revenue
* bookstore activity

---

# 7. Authentication Pages

## Login

Single login page.

Users:

* Reader
* Librarian
* Library Admin

System automatically redirects based on role.

Fields:

* Email / Phone
* Password

Actions:

* Login
* Forgot Password
* Google Sign In

---

## Reader Signup

Fields:

* Username
* Email
* Password
* Confirm Password

---

## Library Signup

Fields:

* Library Name
* Admin Username
* Email
* Password
* Library Type
* Location

---

# 8. Reader Experience

## Reader Dashboard

Widgets:

### Continue Reading

Shows:

* Cover
* Title
* Progress
* Resume Button

---

### Reading Statistics

Displays:

* Books Owned
* Books Finished
* Reading Hours
* Current Reads

---

### Recommended Books

Displays:

* Cover
* Title
* Author

---

### Recent Purchases

Displays:

* Book Covers
* Purchase Date

---

# 9. Digital Bookstore

## Book Grid

Each card displays:

* Cover
* Title
* Author
* Price
* Rating

Actions:

* View Details
* Add Favorite

---

## Search Filters

Search:

* Title
* Author

Filters:

* Category
* Price
* Rating

---

## Book Details Page

Displays:

* Cover
* Description
* Author
* Rating
* Reviews
* Price

Actions:

* Purchase
* Favorite

---

# 10. Reader Library

Displays purchased books.

View Modes:

* Grid
* List

Actions:

* Read
* View Progress

---

# 11. Book Reader

Layout:

```text
Top Reader Toolbar
Book Content
Bottom Progress Bar
```

Features:

* Bookmark
* Fullscreen
* Zoom
* Progress Tracking

---

# 12. Library Dashboard

## Overview Cards

Displays:

* Total Books
* Active Loans
* Overdue Books
* Fines Due

---

## Charts

Displays:

* Borrowing Trends
* Fine Collection
* Inventory Growth

---

## Recent Activity

Displays:

* Books Issued
* Books Returned
* New Borrowers

---

# 13. Books Module

Table Columns:

* Title
* Author
* ISBN
* Copies
* Available
* Status

Actions:

* Add Book
* Edit
* Delete
* OCR Scan

---

## Add Book Modal

Methods:

* Manual Entry
* ISBN Scan
* Cover Scan

Fields:

* Title
* Author
* ISBN
* Copies

---

# 14. Borrowers Module

Table Columns:

* Name
* Membership ID
* Status
* Active Loans

Actions:

* Register Borrower
* View History
* Edit

---

## Register Borrower

Methods:

* Manual Entry
* Student ID Scan

Fields:

* Name
* Admission Number
* Contact

---

# 15. Loans Module

Table Columns:

* Borrower
* Book
* Borrow Date
* Due Date
* Status

Actions:

* Issue Book
* Return Book

---

## Issue Book Modal

Fields:

* Borrower
* Book
* Due Date

---

# 16. Fines Module

Cards:

* Today's Collections
* Monthly Collections
* Outstanding Fines

Table:

* Borrower
* Amount
* Status

Actions:

* Mark Paid

---

# 17. OCR Interface

Upload Area:

* Drag and Drop
* Browse File

---

Processing States:

* Uploading
* Processing
* Extracting
* Review
* Complete

---

Results Panel

Displays extracted:

* Title
* Author
* ISBN

Editable before saving.

---

# 18. Notifications Center

Tabs:

* Sent
* Pending
* Failed

Displays:

* Recipient
* Channel
* Status
* Date

---

# 19. Analytics Dashboard

Library Admin View

Charts:

* Borrow Trends
* Inventory Growth
* Fine Revenue

---

Super Admin View

Charts:

* Revenue
* Tenant Growth
* Marketplace Growth
* Active Readers

---

# 20. Super Admin Dashboard

Navigation:

* Overview
* Tenants
* Marketplace
* Revenue
* Analytics
* Settings

---

## Overview

Cards:

* Total Revenue
* Total Tenants
* Active Users
* Marketplace Books

---

## Tenants

Table:

* Library Name
* Status
* Plan
* Created Date

Actions:

* Activate
* Suspend
* View

---

## Marketplace

Table:

* Cover
* Title
* Author
* Price

Actions:

* Upload
* Edit
* Remove

---

# 21. Common Components

Buttons

Variants:

* Primary
* Secondary
* Ghost
* Danger

---

Forms

Components:

* Input
* Select
* Date Picker
* Search Box
* File Upload

---

Tables

Features:

* Pagination
* Sorting
* Filtering
* Search

---

Modals

Used for:

* Create
* Edit
* Confirm Delete
* Payment Actions

---

# 22. Responsive Requirements

Desktop

≥ 1024px

---

Tablet

768px – 1023px

---

Mobile

≤ 767px

Sidebar collapses into drawer.

Tables become card layouts.

Charts become stacked views.

---

# 23. Animation Guidelines

Use animation sparingly.

Allowed:

* Hover states
* Page transitions
* Loading skeletons
* Drawer transitions
* Modal transitions

Avoid:

* Excessive parallax
* Constant motion
* Distracting effects

---

# 24. Empty States

Every module must include:

* Empty State Illustration
* Helpful Message
* CTA Button

Example:

"No books have been added yet."

Button:

"Add First Book"

---

# 25. Loading States

Use:

* Skeleton Loaders
* Progress Indicators
* Processing Status Messages

Never show blank screens.
