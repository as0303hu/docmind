import pytest
import fitz

@pytest.fixture
def sample_pdf_bytes():
    """Minimal valid PDF for testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72,72),"This is a test document. \n\n It has multiple paragraphs. \n\n Third paragraph here.")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes