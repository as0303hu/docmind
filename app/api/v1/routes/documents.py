import uuid
from fastapi import APIRouter, Depends,HTTPException,UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.dependencies import (
    get_chunker,
    get_embedding_service,
    get_pdf_parser,
    get_vector_store,
)

from app.models.schemas import(
    DocumentListResponse,
    DocumentListItem,
    DocumentUploadResponse
)

router = APIRouter(prefix="/documents",tag=["documents"])

@router.post("/upload",response_model=DocumentUploadResponse)
async def upload_document(
    file:UploadFile,
    db:AsyncSession = Depends(get_db),
    pdf_parser=Depends(get_pdf_parser),
    chunker=Depends(get_chunker),
    embedding_service = Depends(get_embedding_service),
    vector_store =Depends(get_vector_store),
):
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400,detail="Only PDF files are supported")
    
    pdf_bytes = await file.read()
    file_size = len(pdf_bytes)
    
    pages = pdf_parser.extract_pages(pdf_bytes)
    if not pages:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")
    
    page_count = pdf_parser.get_page_count(pdf_bytes)
    chunks = chunker.chunk_pages(pages)
    texts = [chunk.content for chunk in chunks]
    embeddings = await embedding_service.generate_embeddings_batch(texts)
    
    await vector_store.ensure_pgvector_extension(db)
    document = await vector_store.store_document(
        db=db,
        filename=file.filename,
        file_size=file_size,
        page_count=page_count,
        chunks = chunks,
        embeddings=embeddings,
    )
    
    return DocumentUploadResponse.model_validate(document)

@router.get("",response_model=DocumentListResponse)
async def llist_documents(
    db:AsyncSession = Depends(get_db),
    vector_store = Depends(get_vector_store),
    ):
    documents = await vector_store.get_all_documents(db)
    return DocumentListResponse(
        documents=[DocumentListItem.model_validate(doc) for doc in documents],
        total_count=len(documents),
    )

@router.get("/{document_id}",response_model=DocumentUploadResponse)
async def get_document(
    document_id: uuid.UUID,
    db:AsyncSession=Depends(get_db),
    vector_store = Depends(get_vector_store),
):
    document = await vector_store.get_document_by_id(db,document_id)
    if not document:
        raise HTTPException(status_code=404,detail="Document not found")
    return DocumentUploadResponse.model_validate(document)

@router.delete("/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    db:AsyncSession = Depends(get_db),
    vector_store = Depends(get_vector_store),
):
    deleted = await vector_store.delete_document(db,document_id)
    if not deleted:
        raise HTTPException(status_code=404,detail ="Document not found")
    return {"detail":"Document Deleted Succesfully"}
    
    
    