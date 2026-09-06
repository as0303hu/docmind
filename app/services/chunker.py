
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.services.pdf_parser import PDFPage
from app.core.logging import get_logger

logger = get_logger(__name__)

class TextChunk:
    def __init__(self,content:str,page_number:int,chunk_index:int):
        self.content = content
        self.page_number = page_number
        self.chunk_index = chunk_index

class TextChunker:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function = len,
            separators=["\n\n", "\n", ".", " ",""],
        )
    
    def chunk_pages(self,pages:list[PDFPage])-> list[TextChunk]:
        chunks = []
        chunk_index = 0
        
        for page in pages:
            page_chunks = self.splitter.split_text(page.text)
            for text in page_chunks:
                chunks.append(
                    TextChunk(
                        content=text,
                        page_number = page.page_number,
                        chunk_index=chunk_index
                    )
                )
                chunk_index +=1
        
        logger.info(
            "text_chunked",
            total_pages = len(pages),
            total_chunks = len(chunks)
        )
        return chunks