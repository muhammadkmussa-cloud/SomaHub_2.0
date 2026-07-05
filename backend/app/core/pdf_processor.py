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

try:
    import fitz
except ImportError:
    fitz = None

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


def _is_bbox_inside_any_visual(bbox, visuals) -> bool:
    if not fitz:
        return False
    b_rect = fitz.Rect(bbox)
    b_area = b_rect.width * b_rect.height
    if b_area <= 0:
        return False
    for v in visuals:
        v_rect = v["rect"]
        intersect = b_rect & v_rect
        if not intersect.is_empty:
            intersect_area = intersect.width * intersect.height
            if intersect_area > b_area * 0.5:
                return True
    return False


def _extract_visuals_from_page(
    page, doc, page_num: int, media_dir: Path, ebook_prefix: str, url_prefix: str
) -> list[dict]:
    """
    Extract raster images and vector drawing clusters (charts/graphs/diagrams)
    from a page and save them. Returns metadata list.

    Args:
        page: PyMuPDF page object.
        doc: PyMuPDF document object.
        page_num: Zero-based page index.
        media_dir: Local filesystem directory where images are saved.
        ebook_prefix: Unique prefix per ebook (e.g. hex of ebook UUID) to avoid filename collisions.
        url_prefix: URL directory prefix for generated image URLs (e.g. "/uploads/ebooks/media").
    """
    visuals = []
    if not fitz:
        return visuals

    # 1. Raster images
    try:
        images_info = page.get_images(full=True)
    except Exception:
        images_info = []

    for img_info in images_info:
        xref = img_info[0]
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        rect = rects[0]

        try:
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            ext = base_image["ext"]
            filename = f"{ebook_prefix}_img_p{page_num}_{xref}.{ext}"
            file_path = media_dir / filename
            file_path.write_bytes(img_bytes)
            url = f"{url_prefix}/{filename}"
            visuals.append({
                "type": "image",
                "rect": rect,
                "url": url,
                "alt": f"Image on Page {page_num + 1}"
            })
        except Exception as e:
            logger.warning("Failed to extract raster image on page %d (xref %d): %s", page_num, xref, e)

    # 2. Vector drawings (graphs, charts, diagrams)
    try:
        drawings = page.get_drawings()
    except Exception:
        drawings = []

    drawing_rects = []
    page_width = page.rect.width
    page_height = page.rect.height

    for path in drawings:
        p_rect = path.get("rect")
        if not p_rect or p_rect.is_empty:
            continue
        # Skip full page background rects
        if p_rect.width > page_width * 0.95 and p_rect.height > page_height * 0.95:
            continue
        # Skip full width thin horizontal separators
        if p_rect.width > page_width * 0.8 and p_rect.height < 3:
            continue
        drawing_rects.append(p_rect)

    # Cluster overlapping/nearby rectangles
    clusters = []
    for r in drawing_rects:
        merged = False
        for i, cluster in enumerate(clusters):
            # Dilate cluster manually by 15 points to merge close-by elements
            dilated = fitz.Rect(cluster.x0 - 15, cluster.y0 - 15, cluster.x1 + 15, cluster.y1 + 15)
            if dilated.intersects(r):
                clusters[i] = cluster | r
                merged = True
                break
        if not merged:
            clusters.append(r)

    # Render each substantial cluster as a chart image
    chart_idx = 1
    for cluster in clusters:
        # Constrain to page boundaries
        cluster = cluster & page.rect
        # Filter out page borders that encompass almost the entire page
        if cluster.width > page_width * 0.9 and cluster.height > page_height * 0.9:
            continue
        if cluster.width > 50 and cluster.height > 50:
            try:
                # 2x zoom render for clear charts/graphs
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), clip=cluster)
                filename = f"{ebook_prefix}_chart_p{page_num}_{chart_idx}.png"
                file_path = media_dir / filename
                pix.save(str(file_path))
                
                url = f"{url_prefix}/{filename}"
                visuals.append({
                    "type": "chart",
                    "rect": cluster,
                    "url": url,
                    "alt": f"Chart/Diagram {chart_idx} on Page {page_num + 1}"
                })
                chart_idx += 1
            except Exception as e:
                logger.warning("Failed to render chart cluster on page %d: %s", page_num, e)

    return visuals


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
    list_item_lines: list[str] = []
    current_list_marker = ""
    current_list_indent = ""
    current_list_type = ""  # "bullet" or "number"
    
    def flush_para() -> None:
        """Push accumulated standard body text lines as a paragraph block."""
        if not para_lines:
            return
        combined = " ".join(para_lines).strip()
        combined = re.sub(r"-\s+", "", combined)
        if combined:
            combined = _capitalize_sentences(combined)
            output.append(combined)
        para_lines.clear()

    def flush_blockquote() -> None:
        """Push accumulated blockquote lines as a blockquote block."""
        if not blockquote_lines:
            return
        combined = " ".join(blockquote_lines).strip()
        combined = re.sub(r"-\s+", "", combined)
        if combined:
            combined = _capitalize_sentences(combined)
            output.append(f"> {combined}")
        blockquote_lines.clear()

    def flush_list_item() -> None:
        """Push accumulated list item lines as a list item block."""
        if not list_item_lines:
            return
        combined = " ".join(list_item_lines).strip()
        combined = re.sub(r"-\s+", "", combined)
        if combined:
            combined = _capitalize_sentences(combined)
            if current_list_type == "bullet":
                output.append(f"{current_list_indent}- {combined}")
            else:
                output.append(f"{current_list_indent}{current_list_marker}. {combined}")
        list_item_lines.clear()

    def flush_all() -> None:
        flush_para()
        flush_blockquote()
        flush_list_item()

    # Ensure media directory exists and derive a unique prefix per ebook
    media_dir = Path("uploads/ebooks/media")
    media_dir.mkdir(parents=True, exist_ok=True)
    # Use the PDF filename stem (UUID hex from storage) as unique prefix
    ebook_prefix = path.stem
    url_prefix = "/uploads/ebooks/media"

    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        y_top_limit = page_height * 0.08
        y_bottom_limit = page_height * 0.92
        
        # Get visual elements (images, charts, diagrams)
        visuals = _extract_visuals_from_page(
            page, doc, page_num, media_dir, ebook_prefix, url_prefix
        )
        
        # Get text blocks
        blocks = page.get_text("dict", sort=True).get("blocks", [])
        
        # Merge text blocks and visuals
        items = []
        for block in blocks:
            if block.get("type") == 0:
                bbox = block.get("bbox", (0, 0, 0, 0))
                if _is_bbox_inside_any_visual(bbox, visuals):
                    continue
                items.append({
                    "type": "text",
                    "y": bbox[1],
                    "x": bbox[0],
                    "data": block
                })
        for v in visuals:
            rect = v["rect"]
            items.append({
                "type": "visual",
                "y": rect.y0,
                "x": rect.x0,
                "data": v
            })
            
        # Sort items by y-coordinate, then x-coordinate to handle columns/side-by-side elements
        items.sort(key=lambda item: (item["y"], item["x"]))

        for item in items:
            if item["type"] == "visual":
                flush_all()
                v = item["data"]
                output.append(f"\n![{v['alt']}]({v['url']})\n")
                in_list = False
                block_is_blockquote = None
                continue

            block = item["data"]

            # Reset block state at block boundary
            in_list = False
            block_is_blockquote = None
            flush_all()

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
                    block_is_blockquote = None
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
                    block_is_blockquote = None
                    
                    current_list_indent = indent
                    if bullet_match:
                        current_list_type = "bullet"
                        current_list_marker = "-"
                        content = bullet_match.group(2).strip()
                        list_item_lines.append(content)
                    else:
                        current_list_type = "number"
                        current_list_marker = number_match.group(1)
                        content = number_match.group(2).strip()
                        list_item_lines.append(content)
                
                elif in_list:
                    # Continuation of list item inside the same layout block
                    list_item_lines.append(line_text)
                
                else:
                    # Regular body text or blockquote
                    in_list = False
                    
                    if block_is_blockquote is None:
                        block_is_blockquote = (line_x0 > body_left_margin + 20)
                    
                    if block_is_blockquote:
                        flush_para()
                        blockquote_lines.append(line_text)
                    else:
                        flush_blockquote()
                        para_lines.append(line_text)
                        
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
    full = "\n".join(line if line.strip() else "" for line in full.splitlines())

    return full.strip() or None
