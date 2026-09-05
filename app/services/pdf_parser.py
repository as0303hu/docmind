
import fitz
from app.core.logging import get_logger

logger = get_logger(__name__)

class PDFPage:
    """Reperesents a single psge of extracted text from s PDF"""
    def __init__(self,page_number:int,text:str):
        self.page_number = page_number
        self.text = text
    
    def __repr__(self):
        preview = self.text[:50] +"..." if len(self.text)>50 else self.text
        return f"PDFPage(page={self.page_number}, text='{preview}')"

class PDFParser:
    """Extractd text from PDF files using PyMuPDF (fitz)."""
    def extract_pages(self,pdf_bytes:bytes)-> list[PDFPage]:
        """Extract text from each page of a pdf"""
        try:
            doc = fitz.open(stream=pdf_bytes,filetype="pdf")
        except Exception as e:
            raise RuntimeError(f"Failed to open PDF: {e}") from e
        
        pages: list[PDFPage] =[]
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            raw_text = page.get_text("text")
            cleaned_text = self._clean_text(raw_text)
            if cleaned_text.strip():
                pages.append(PDFPage(page_number=page_num+1, text=cleaned_text))
        doc.close()
        
        logger.info(
            "PDF parsed",
            total_pages = len(doc) if not doc.is_closed else page_num+1,
            pages_with_text = len(pages),
        )
        return pages
    
    def get_page_count(self, pdf_bytes:bytes)-> int:
        """Return the total number of pages in a PDF"""
        
        doc = fitz.open(stream=pdf_bytes,filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    
    def _clean_text(self,text:str)-> str:
        """Clean extracted text by removing empty lines and excess whitespace."""
        
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return "\n".join(cleaned_lines)