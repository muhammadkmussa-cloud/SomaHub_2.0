"""
PDF text extraction and structuring using PyMuPDF (fitz).

Extracts text from every page, classifies lines as headings (with hierarchy styles)
or body text using font-size thresholds and metadata. Handles lists, sentence capitalization,
blockquotes, bold/italic emphasis, and ignores headers/footers.
"""

from __future__ import annotations

import logging
import re
import statistics
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Regex Patterns ──────────────────────────────────────────────────────────
# Matches bullet characters. Asterisk '*' is only matched if followed by space to avoid matching markdown italic starts.
BULLET_RE = re.compile(
    r"^\s*([•▪◦\-+–—■·●○▫◾◼\u2022\u00b7\u25aa\u25ab\u25cf\u25cb\u25fe\u25fc]|\*(?=\s))\s*(.*)"
)
# Matches numbered/lettered patterns like "1.", "a.", "i.", "1)", "a)"
NUMBER_RE = re.compile(r"^\s*(\d+|[a-zA-Z]|[ivxIVX]+)[\.\)]\s*(.*)")


# ── Helpers ──────────────────────────────────────────────────────────────────

def _span_is_bold(font_name: str) -> bool:
    f_lower = font_name.lower()
    return "bold" in f_lower or f_lower.endswith("-b") or f_lower.endswith("-bd") or "-bold" in f_lower


def _span_is_italic(font_name: str) -> bool:
    f_lower = font_name.lower()
    return "italic" in f_lower or "oblique" in f_lower or f_lower.endswith("-i") or f_lower.endswith("-ob") or "-italic" in f_lower


def _apply_italic(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    leading = text[:len(text) - len(text.lstrip())]
    trailing = text[len(text.rstrip()):]
    if stripped.startswith("*") and stripped.endswith("*"):
        return text
    return f"{leading}*{stripped}*{trailing}"


def _apply_bold(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    leading = text[:len(text) - len(text.lstrip())]
    trailing = text[len(text.rstrip()):]
    if stripped.startswith("**") and stripped.endswith("**"):
        return text
    return f"{leading}**{stripped}**{trailing}"


def _apply_bold_italic(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    leading = text[:len(text) - len(text.lstrip())]
    trailing = text[len(text.rstrip()):]
    if stripped.startswith("***") and stripped.endswith("***"):
        return text
    return f"{leading}***{stripped}***{trailing}"


def _capitalize_first_alpha(s: str) -> str:
    """Capitalize the first alphabetic letter in the string, bypassing leading markdown/list markers."""
    for idx, char in enumerate(s):
        if char.isalpha():
            return s[:idx] + char.upper() + s[idx+1:]
    return s


def _capitalize_sentences(text: str) -> str:
    """Ensure every sentence in the text starts with a capital letter."""
    if not text:
        return text
    # Split text by sentence boundaries (.!? followed by whitespace)
    parts = re.split(r'([.!?]\s+)', text)
    for i in range(0, len(parts), 2):
        if parts[i]:
            parts[i] = _capitalize_first_alpha(parts[i])
    return "".join(parts)


def _is_footer_header_noise(text: str, title: Optional[str] = None, author: Optional[str] = None) -> bool:
    """Detect common header/footer elements like page numbers, author names, or titles."""
    text_clean = text.replace("*", "").strip()
    if not text_clean:
        return True
    
    text_lower = text_clean.lower()
    
    # Page numbers and page markers
    if re.fullmatch(r"\d+", text_clean):
        return True
    if re.fullmatch(r"[ivxIVX]+", text_clean):
        return True
    if re.search(r"\b(page|pg)\b\s*\d+", text_lower):
        return True
    if re.search(r"\b(page|pg)\b", text_lower) and len(text_clean) <= 10:
        return True
    
    # Metadata matches
    if title:
        title_clean = title.lower().strip()
        if title_clean in text_lower or text_lower in title_clean:
            return True
    if author:
        author_clean = author.lower().strip()
        if author_clean in text_lower or text_lower in author_clean:
            return True
            
    # Generic short metadata or noise (often missing sentence end punctuation)
    if len(text_clean) < 40 and not text_clean.endswith("."):
        return True
        
    return False


def _is_likely_heading(
    text: str, avg_size: float, body_size: float, is_bold: bool
) -> tuple[bool, int]:
    """
    Return (is_heading, level) where level is 1, 2, 3 or 4.
    """
    clean_text = text.replace("*", "").strip()
    if len(clean_text) > 120 or not clean_text:
        return False, 0
    
    ratio = avg_size / body_size if body_size else 1.0

    if ratio >= 1.8:
        return True, 1
    if ratio >= 1.5:
        return True, 2
    if ratio >= 1.2:
        return True, 3
    if is_bold and ratio >= 1.05 and len(clean_text) <= 80:
        return True, 4
    if clean_text.isupper() and len(clean_text.split()) <= 10 and len(clean_text) >= 4:
        return True, 3
        
    return False, 0


def _spans_to_text_and_meta(spans: list) -> tuple[str, float, bool]:
    """Merge spans into (text, avg_font_size, has_bold) preserving styles."""
    texts = []
    sizes = []
    has_bold = False

    for s in spans:
        span_text = s.get("text", "")
        if not span_text:
            continue
        font = s.get("font", "")
        size = s.get("size", 12.0)
        sizes.append(size)

        bold = _span_is_bold(font)
        italic = _span_is_italic(font)

        if bold:
            has_bold = True

        # Apply emphasis markup (italics & bold)
        if bold and italic:
            formatted_text = _apply_bold_italic(span_text)
        elif bold:
            formatted_text = _apply_bold(span_text)
        elif italic:
            formatted_text = _apply_italic(span_text)
        else:
            formatted_text = span_text

        texts.append(formatted_text)

    joined_text = "".join(texts)
    avg_size = sum(sizes) / len(sizes) if sizes else 12.0
    return joined_text, avg_size, has_bold


# ── Public API ────────────────────────────────────────────────────────────────

def extract_structured_text(
    file_path: str | Path,
    title: Optional[str] = None,
    author: Optional[str] = None
) -> Optional[str]:
    """
    Extract and structure text from a PDF file.

    Maintains exact order of sentences/words, ignores headers/footers containing
    page numbers/titles/authors, identifies headings with hierarchy style,
    processes lists with proper indentation, capitalizes sentences, and styles
    blockquotes and emphasis.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.error("PyMuPDF is not installed.")
        return None

    path = Path(file_path)
    if not path.exists():
        logger.warning("PDF not found: %s", path)
        return None

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        logger.error("Cannot open PDF %s: %s", path, exc)
        return None

    # ── Pass 1: collect all font sizes and left margins for baselines ─────────
    all_sizes: list[float] = []
    all_x0s: list[float] = []
    
    for page in doc:
        for block in page.get_text("dict", sort=True).get("blocks", []):
            if block.get("type") != 0:
                continue
            all_x0s.append(block.get("bbox", (0, 0, 0, 0))[0])
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        all_sizes.append(float(span.get("size", 12.0)))

    if not all_sizes:
        doc.close()
        return None

    body_size = statistics.median(all_sizes)
    body_left_margin = statistics.median(all_x0s) if all_x0s else 72.0
    logger.debug("Baseline body font size: %.1f pt, left margin: %.1f pt", body_size, body_left_margin)

    # ── Pass 2: extract and structure content ─────────────────────────────────
    output: list[str] = []
    para_lines: list[str] = []
    blockquote_lines: list[str] = []
    
    def flush_para() -> None:
        """Push accumulated standard body text lines as a paragraph block."""
        if not para_lines:
            return
        combined = " ".join(para_lines).strip()
        combined = re.sub(r"-\s+", "", combined)
        if combined:
            output.append(combined)
        para_lines.clear()

    def flush_blockquote() -> None:
        """Push accumulated blockquote lines as a blockquote block."""
        if not blockquote_lines:
            return
        combined = " ".join(blockquote_lines).strip()
        combined = re.sub(r"-\s+", "", combined)
        if combined:
            output.append(f"> {combined}")
        blockquote_lines.clear()

    def flush_all() -> None:
        flush_para()
        flush_blockquote()

    for page in doc:
        page_height = page.rect.height
        y_top_limit = page_height * 0.08
        y_bottom_limit = page_height * 0.92
        
        blocks = page.get_text("dict", sort=True).get("blocks", [])

        for block in blocks:
            if block.get("type") != 0:
                continue

            # Reset list state at block boundary to prevent bleeding list status
            in_list = False
            list_indent = ""

            # Pre-merge lines on the same visual horizontal level to handle split bullets/numbers
            raw_lines = block.get("lines", [])
            merged_lines = []
            for line in raw_lines:
                bbox = line.get("bbox", (0, 0, 0, 0))
                y0, y1 = bbox[1], bbox[3]
                
                # Check if we can merge with the last line in merged_lines
                if merged_lines:
                    prev_line = merged_lines[-1]
                    prev_bbox = prev_line.get("bbox", (0, 0, 0, 0))
                    prev_y0, prev_y1 = prev_bbox[1], prev_bbox[3]
                    
                    overlap_height = min(y1, prev_y1) - max(y0, prev_y0)
                    line_height = y1 - y0
                    prev_height = prev_y1 - prev_y0
                    min_h = min(line_height, prev_height)
                    
                    is_same_level = (abs(y0 - prev_y0) < 4.0) or (min_h > 0 and overlap_height / min_h > 0.5)
                    
                    if is_same_level:
                        all_spans = prev_line.get("spans", []) + line.get("spans", [])
                        all_spans.sort(key=lambda s: s.get("bbox", (0, 0, 0, 0))[0])
                        prev_line["spans"] = all_spans
                        prev_line["bbox"] = (
                            min(prev_bbox[0], bbox[0]),
                            min(prev_y0, y0),
                            max(prev_bbox[2], bbox[2]),
                            max(prev_y1, y1)
                        )
                        continue
                
                merged_lines.append({
                    "bbox": bbox,
                    "spans": list(line.get("spans", []))
                })

            for line in merged_lines:
                spans = line.get("spans", [])
                if not spans:
                    continue

                line_text, avg_size, is_bold = _spans_to_text_and_meta(spans)
                if not line_text.strip():
                    continue

                line_bbox = line.get("bbox", (0, 0, 0, 0))
                
                # Check header/footer margins
                in_header = line_bbox[1] < y_top_limit
                in_footer = line_bbox[3] > y_bottom_limit

                if in_header or in_footer:
                    is_h, _ = _is_likely_heading(line_text, avg_size, body_size, is_bold)
                    if not is_h:
                        if _is_footer_header_noise(line_text, title, author):
                            continue

                # Heading detection
                is_heading, level = _is_likely_heading(line_text, avg_size, body_size, is_bold)
                if is_heading:
                    flush_all()
                    
                    if level == 1:
                        prefix = "#"
                    elif level == 2:
                        prefix = "##"
                    elif level == 3:
                        prefix = "###"
                    else:
                        prefix = "####"

                    header_text = _capitalize_sentences(line_text)
                    output.append(f"\n{prefix} {header_text}\n")
                    in_list = False
                    continue

                # List item detection
                bullet_match = BULLET_RE.match(line_text)
                number_match = NUMBER_RE.match(line_text)
                line_x0 = line_bbox[0]

                # Determine list item indentation level
                if line_x0 > body_left_margin + 24:
                    indent = "        "
                elif line_x0 > body_left_margin + 12:
                    indent = "    "
                else:
                    indent = ""

                if bullet_match or number_match:
                    flush_all()
                    in_list = True
                    list_indent = indent
                    
                    if bullet_match:
                        content = bullet_match.group(2).strip()
                        content = _capitalize_sentences(content)
                        output.append(f"{indent}- {content}")
                    else:
                        num_prefix = number_match.group(1)
                        content = number_match.group(2).strip()
                        content = _capitalize_sentences(content)
                        output.append(f"{indent}{num_prefix}. {content}")
                
                elif in_list:
                    # Continuation of list item inside the same layout block
                    content = _capitalize_sentences(line_text)
                    if output:
                        output[-1] = f"{output[-1]} {content}"
                    else:
                        output.append(f"{list_indent}  {content}")
                
                else:
                    # Regular body text or blockquote
                    in_list = False
                    is_blockquote = (line_x0 > body_left_margin + 20)
                    content = _capitalize_sentences(line_text)
                    
                    if is_blockquote:
                        flush_para()
                        blockquote_lines.append(content)
                    else:
                        flush_blockquote()
                        para_lines.append(content)
                        
                        # Sentence-final punctuation indicates paragraph end boundaries
                        sentence_end = line_text[-1] in ".!?…\u201d\u2019" if line_text else False
                        if sentence_end:
                            flush_para()

            # Flush block boundaries
            flush_all()

    doc.close()

    if not output:
        return None

    # ── Final styling & formatting cleanup ────────────────────────────────────
    full = "\n\n".join(output)
    
    # Correct spacing issues around bullet / numbered lists
    # Group consecutive list items under a single newline separation
    lines = full.splitlines()
    cleaned_lines = []
    
    for idx, line in enumerate(lines):
        striped = line.strip()
        # If this line is a list item and previous line was also a list item
        if idx > 0 and (striped.startswith("-") or (striped and striped[0].isdigit() and "." in striped)):
            if cleaned_lines:
                prev_striped = cleaned_lines[-1].strip()
                if prev_striped.startswith("-") or (prev_striped and prev_striped[0].isdigit() and "." in prev_striped):
                    # Remove empty line before list item
                    if cleaned_lines and cleaned_lines[-1] == "":
                        cleaned_lines.pop()
        cleaned_lines.append(line)

    # Collapse multiple spaces while preserving leading indentation space tokens
    for idx, line in enumerate(cleaned_lines):
        leading_ws = re.match(r"^\s*", line).group(0)
        content = line[len(leading_ws):]
        content = re.sub(r"[ \t]{2,}", " ", content)
        cleaned_lines[idx] = leading_ws + content

    full = "\n".join(cleaned_lines)
    full = re.sub(r"\n{3,}", "\n\n", full)
    full = "\n".join(l if l.strip() else "" for l in full.splitlines())

    return full.strip() or None
