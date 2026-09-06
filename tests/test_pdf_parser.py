from app.services.pdf_parser import PDFParser


def test_extract_pages_returns_pages(sample_pdf_bytes):
    parser = PDFParser()
    pages = parser.extract_pages(sample_pdf_bytes)

    assert len(pages) > 0
    assert pages[0].page_number == 1
    assert "test document" in pages[0].text.lower()


def test_get_page_count(sample_pdf_bytes):
    parser = PDFParser()
    count = parser.get_page_count(sample_pdf_bytes)

    assert count == 1


def test_extract_pages_empty_pdf():
    import fitz

    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    parser = PDFParser()
    pages = parser.extract_pages(pdf_bytes)

    assert len(pages) == 0