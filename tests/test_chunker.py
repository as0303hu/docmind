from app.services.chunker import TextChunker
from app.services.pdf_parser import PDFPage


def test_chunk_pages_creates_chunks():
    chunker = TextChunker()
    pages = [
        PDFPage(page_number=1, text="A" * 2000),
    ]
    chunks = chunker.chunk_pages(pages)

    assert len(chunks) > 1
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_chunk_pages_preserves_page_numbers():
    chunker = TextChunker()
    pages = [
        PDFPage(page_number=1, text="Page one content. " * 100),
        PDFPage(page_number=2, text="Page two content. " * 100),
    ]
    chunks = chunker.chunk_pages(pages)

    page_numbers = set(chunk.page_number for chunk in chunks)
    assert 1 in page_numbers
    assert 2 in page_numbers


def test_chunk_pages_small_text_single_chunk():
    chunker = TextChunker()
    pages = [PDFPage(page_number=1, text="Short text.")]
    chunks = chunker.chunk_pages(pages)

    assert len(chunks) == 1
    assert chunks[0].content == "Short text."