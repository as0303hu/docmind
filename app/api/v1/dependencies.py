from app.services.embeddings import EmbeddingService
from app.services.pdf_parser import PDFParser
from app.services.chunker import TextChunker
from app.services.vector_store import VectorStore
from app.services.qa_chain import QAService

def get_pdf_parser()-> PDFParser:
    return PDFParser()


def get_chunker()-> TextChunker:
    return TextChunker()

def get_embedding_service()-> EmbeddingService:
    return EmbeddingService()

def get_vector_store()-> VectorStore:
    return VectorStore()

def get_qa_service() ->QAService:
    return QAService()