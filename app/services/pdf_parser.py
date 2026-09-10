"""PDF parsing service using PyMuPDF (fitz)."""
import fitz

from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFPage:
    """Reperesents a single psge of extracted text from s PDF"""

    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text


class PDFParser:
    """Extractd text content from PDF files page by page."""

    def extract_pages(self, pdf_bytes: bytes) -> list[PDFPage]:
        """Parse a PDF and return pages that contain text."""
        doc = fitz.open(stream=pdf_bytes, filetype="pfd")
        pages =[]
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            cleaned_text = self._clean_text(text)
            if cleaned_text.strip():
                pages.append(PDFPage(page_number=page_num + 1, text=cleaned_text))
        doc.close()

        logger.info(
            "PDF parsed",
            total_pages=len(doc) if not doc.is_closed else page_num + 1,
            pages_with_text=len(pages),
        )
        return pages

    def get_page_count(self, pdf_bytes: bytes) -> int:
        """Return the total number of pages in a PDF"""

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count

    def _clean_text(self, text: str) -> str:
        """Clean extracted text by removing empty lines and excess whitespace."""

        lines = text.split("\n")
        cleaned_lines =[]
        for line in lines:
            stripped = line.strip()
            if stripped:
                cleaned_lines.append(stripped)
        return "\n".join(cleaned_lines)
