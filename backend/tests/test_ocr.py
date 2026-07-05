import time
import pytest
from unittest.mock import AsyncMock, patch
from app.ai.ocr import OCRPipeline
from app.ai.text_extractor import TextExtractor

# Mock responses representing optimal and degraded lighting conditions
MOCK_OPTIMAL_COVER_JSON = """
{
  "title": "Clean Code",
  "subtitle": "A Handbook of Agile Software Craftsmanship",
  "authors": ["Robert C. Martin"],
  "publisher": "Prentice Hall",
  "isbn": "9780132350884",
  "publication_year": 2008,
  "edition": "1st",
  "language": "English",
  "categories": ["Software Engineering"],
  "description": "A handbook of agile software craftsmanship.",
  "subjects": ["Programming"]
}
"""

# Low light scenario - might contain slightly messy whitespace or minor markdown surrounding it
MOCK_LOW_LIGHT_COVER_JSON = """
Here is the JSON model extracted from low light conditions:
```json
{
  "title": "Clean Code",
  "subtitle": "A Handbook of Agile Software Craftsmanship",
  "authors": ["Robert C. Martin"],
  "publisher": "Prentice Hall",
  "isbn": "9780132350884",
  "publication_year": 2008,
  "edition": "1st",
  "language": "English",
  "categories": ["Software Engineering"],
  "description": "A handbook of agile software craftsmanship.",
  "subjects": ["Programming"]
}
```
"""

# Glare scenario - might have partial text occlusion or conversational responses
MOCK_GLARE_COVER_JSON = """
The image has significant glare. However, I was able to extract the following:
{
  "title": "Clean Code",
  "subtitle": null,
  "authors": ["Robert C. Martin"],
  "publisher": "Prentice Hall",
  "isbn": "9780132350884",
  "publication_year": null,
  "edition": null,
  "language": "English",
  "categories": [],
  "description": null,
  "subjects": []
}
"""

# ID Card scenarios (simulated student / national ID metadata)
MOCK_STUDENT_ID_JSON = """
{
  "title": "Muhammad Mussa",
  "subtitle": null,
  "authors": [],
  "publisher": null,
  "isbn": "STD-99881122",
  "publication_year": null,
  "edition": null,
  "language": null,
  "categories": [],
  "description": null,
  "subjects": []
}
"""


@pytest.mark.asyncio
async def test_ocr_accuracy_optimal_lighting():
    """Verify OCR accuracy under optimal lighting conditions."""
    pipeline = OCRPipeline()
    
    with patch.object(pipeline.client, "vision", new_callable=AsyncMock) as mock_vision:
        # Mocking extract_book_metadata, generate_description, and extract_isbn calls
        mock_vision.side_effect = [
            MOCK_OPTIMAL_COVER_JSON,                        # extract_book_metadata
            "A handbook of agile software craftsmanship.",  # generate_description
            "9780132350884"                                 # extract_isbn
        ]
        
        start_time = time.perf_counter()
        metadata = await pipeline.process_book_image(b"fake_image_content")
        duration = time.perf_counter() - start_time
        
        # Accuracy Assertions
        assert metadata["title"] == "Clean Code"
        assert "Robert C. Martin" in metadata["authors"]
        assert metadata["isbn"] == "9780132350884"
        assert metadata["publication_year"] == 2008
        
        # Speed/Latency Verification (should be fast in unit tests)
        assert duration < 1.0  # SLA limit of 1.0 second for local execution


@pytest.mark.asyncio
async def test_ocr_low_light_conditions():
    """Verify that OCR can parse book metadata correctly even in low light (simulated via formatting noise)."""
    pipeline = OCRPipeline()
    
    with patch.object(pipeline.client, "vision", new_callable=AsyncMock) as mock_vision:
        mock_vision.side_effect = [
            MOCK_LOW_LIGHT_COVER_JSON,
            "A handbook of agile software craftsmanship.",
            "9780132350884"
        ]
        
        metadata = await pipeline.process_book_image(b"fake_image_content_low_light")
        
        # Verify that parsing correctly strips surrounding text/markdown blocks
        assert metadata["title"] == "Clean Code"
        assert metadata["isbn"] == "9780132350884"
        assert "Robert C. Martin" in metadata["authors"]


@pytest.mark.asyncio
async def test_ocr_glare_conditions():
    """Verify OCR recovery and fallback when glare occludes some fields (simulated via missing values)."""
    pipeline = OCRPipeline()
    
    with patch.object(pipeline.client, "vision", new_callable=AsyncMock) as mock_vision:
        mock_vision.side_effect = [
            MOCK_GLARE_COVER_JSON,
            "A handbook of agile software craftsmanship.",
            "9780132350884"
        ]
        
        metadata = await pipeline.process_book_image(b"fake_image_content_glare")
        
        # Key fields (title, authors, isbn) should be recovered; missing fields gracefully map to None or fallback
        assert metadata["title"] == "Clean Code"
        assert metadata["isbn"] == "9780132350884"
        assert metadata["subtitle"] is None
        assert metadata["publication_year"] is None


@pytest.mark.asyncio
async def test_ocr_student_id_scan():
    """Verify OCR can scan and parse Student/National ID cards for borrower registration."""
    pipeline = OCRPipeline()
    
    with patch.object(pipeline.client, "vision", new_callable=AsyncMock) as mock_vision:
        mock_vision.side_effect = [
            MOCK_STUDENT_ID_JSON,
            "Student ID card containing name and ID number.",
            "STD-99881122"
        ]
        
        metadata = await pipeline.process_book_image(b"fake_student_id_card")
        
        # Student ID should map title to name, isbn to student_id
        assert metadata["title"] == "Muhammad Mussa"
        assert metadata["isbn"] == "STD-99881122"


@pytest.mark.asyncio
async def test_ocr_api_endpoints(async_client, librarian_headers):
    """Integration test verifying API endpoints for OCR cover and student ID scans."""
    from app.main import app
    from app.modules.ocr.router import get_ocr_pipeline

    mock_pipeline = AsyncMock()
    mock_pipeline.process_book_image.return_value = {
        "title": "Clean Code",
        "subtitle": "Handbook",
        "authors": ["Robert C. Martin"],
        "publisher": "Prentice Hall",
        "isbn": "9780132350884",
        "publication_year": 2008,
        "edition": "1st",
        "language": "English",
        "categories": ["Software"],
        "description": "Agile software.",
        "subjects": ["Programming"]
    }
    
    app.dependency_overrides[get_ocr_pipeline] = lambda: mock_pipeline

    try:
        # 1. Test Book Cover Scanning
        files = {"file": ("cover.jpg", b"fake_jpeg_content", "image/jpeg")}
        resp = await async_client.post("/api/v1/ocr/book-cover", files=files, headers=librarian_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Clean Code"
        assert data["isbn"] == "9780132350884"

        # 2. Test Student ID Scanning
        files = {"file": ("id_card.png", b"fake_png_content", "image/png")}
        resp = await async_client.post("/api/v1/ocr/student-id", files=files, headers=librarian_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Clean Code"
        assert data["student_id"] == "9780132350884"
    finally:
        app.dependency_overrides.pop(get_ocr_pipeline, None)
