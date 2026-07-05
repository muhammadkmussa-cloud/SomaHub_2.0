import pytest
from pathlib import Path
import fitz  # PyMuPDF
from app.core.pdf_processor import extract_structured_text

def test_extract_structured_text_missing_file():
    """Verify that None is returned when the file does not exist."""
    assert extract_structured_text("nonexistent_file.pdf") is None

def test_extract_structured_text_valid_pdf(tmp_path: Path):
    """
    Generate a simple PDF with headers, lists, footers, blockquotes, and emphasis,
    and verify that extract_structured_text parses and structures it correctly.
    """
    pdf_path = tmp_path / "test_book.pdf"
    
    # Create a simple PDF document (using default page size 595 x 842)
    doc = fitz.open()
    page = doc.new_page()
    
    # Write a Level 1 heading (fontsize=24)
    page.insert_text(
        fitz.Point(72, 100),
        "introduction to somahub",  # lowercase to verify capitalization
        fontsize=24,
        fontname="helv",
    )
    
    # Write some body text (normal size 12, standard left margin=72)
    page.insert_text(
        fitz.Point(72, 150),
        "somahub is a digital bookstore platform designed to deliver premium experiences.",
        fontsize=12,
        fontname="helv",
    )
    
    # Write a bulleted list item (starts with a bullet character)
    page.insert_text(
        fitz.Point(72, 200),
        "• first feature: high fidelity pdf rendering.",
        fontsize=12,
        fontname="helv",
    )
    
    # Write an indented numbered list item (starts with a number)
    page.insert_text(
        fitz.Point(90, 225),  # indented x0=90 (body_left_margin + 18)
        "1. second feature: vintage-serif reading mode.",
        fontsize=12,
        fontname="helv",
    )
    
    # Write a blockquote block (indented x0=110, no list bullet)
    page.insert_text(
        fitz.Point(110, 260),  # x0=110 (body_left_margin + 38)
        "accessibility is not a nice-to-have, it is a core feature of design.",
        fontsize=12,
        fontname="helv",
    )
    
    # Write a paragraph with bold and italic words
    page.insert_text(
        fitz.Point(72, 300),
        "This paragraph contains ",
        fontsize=12,
        fontname="helv",
    )
    page.insert_text(
        fitz.Point(200, 300),
        "bold text",
        fontsize=12,
        fontname="hebo",  # bold
    )
    page.insert_text(
        fitz.Point(250, 300),
        " and ",
        fontsize=12,
        fontname="helv",
    )
    page.insert_text(
        fitz.Point(280, 300),
        "italic text",
        fontsize=12,
        fontname="helv",
        # We can't set italic fonts easily if helv doesn't have it built-in, but we can verify our mapper!
    )
    
    # Write header/footer elements that should be ignored
    # Header zone: y < 67 (8% of 842)
    page.insert_text(
        fitz.Point(72, 40),
        "SomaHub Documentation Header Info",
        fontsize=10,
        fontname="helv",
    )
    # Footer zone: y > 774 (92% of 842)
    page.insert_text(
        fitz.Point(72, 800),
        "Notes Prepared by Peninah J. Limo Page 1",
        fontsize=9,
        fontname="helv",
    )
    
    doc.save(str(pdf_path))
    doc.close()
    
    # Extract structured text
    structured_content = extract_structured_text(pdf_path, title="SomaHub Documentation", author="Peninah J. Limo")
    assert structured_content is not None
    
    # 1. Verify Level 1 heading (prefix is # and capitalized)
    assert "# Introduction to somahub" in structured_content
    
    # 2. Verify sentence capitalization
    assert "Somahub is a digital bookstore" in structured_content
    
    # 3. Verify list bullet formatting & capitalization
    assert "- First feature: high fidelity pdf rendering." in structured_content
    
    # 4. Verify indented numbered list formatting & capitalization
    # Since x0=90 is indented, it should have 4 spaces prefix:
    assert "    1. Second feature: vintage-serif reading mode." in structured_content
    
    # 5. Verify blockquote formatting (starts with > and capitalized)
    assert "> Accessibility is not a nice-to-have, it is a core feature of design." in structured_content
    
    # 6. Verify bold formatting (wrapped in **)
    assert "**bold text**" in structured_content
    
    # 7. Verify header/footer noise suppression
    assert "SomaHub Documentation Header Info" not in structured_content
    assert "Notes Prepared by Peninah" not in structured_content
    assert "Page 1" not in structured_content
