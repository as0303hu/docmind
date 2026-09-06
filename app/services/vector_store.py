import uuid
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import  settings
from app.core.logging import get_logger
from app.models.domain import Chunk, Document
from app.services.chunker import TextChunk

logger = get_logger(__name__)

class VectorStore:
    async def ensure_pgvector_extension(self,db:AsyncSession)->None:
        await db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await db.commit()
        
    
    async def store_document(
        self,
        db:AsyncSession,
        filename: str,
        file_size:int,
        page_count:int,
        chunks: list[TextChunk],
        embeddings:list[list[float]],
    )->Document:
        document = Document(
            filename=filename,
            file_size=file_size,
            page_count=page_count,
            chunk_count = len(chunks),
        )
        
        db.add(document)
        await db.flush()

        # Add chunks (if any) and commit once
        for chunk, embedding in zip(chunks, embeddings):
            db_chunk = Chunk(
                document_id=document.id,
                content=chunk.content,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                embedding=embedding,
            )
            db.add(db_chunk)

        await db.commit()
        await db.refresh(document)

        logger.info(
            "document_stored",
            document_id=str(document.id),
            filename=filename,
            chunk_count=len(chunks),
        )

        return document
    
    async def similarity_search(
        self, 
        db:AsyncSession,
        query_embedding:list[float],
        top_k:int = settings.top_k,
        )->list[tuple[Chunk,float]]:
        distance = Chunk.embedding.cosine_distance(query_embedding).label(
            "distance"
        )
        stmt = select(Chunk,distance).order_by(distance).limit(top_k)
        result = await db.execute(stmt)
        rows = result.all()
        
        return [(chunk,1-dist) for chunk,dist in rows]
    
    async def get_all_documents(self, db:AsyncSession)-> list[Document]:
        stmt = select(Document).order_by(Document.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_document_by_id(
        self,db:AsyncSession, document_id:uuid.UUID
    )-> Document| None:
        stmt = select(Document).where(Document.id== document_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete_document(
        self,db:AsyncSession, document_id:uuid.UUID
    )->bool:
        document = await self.get_document_by_id(db,document_id)
        if not document:
            return False
        await db.delete(document)
        await db.commit()
        logger.info("document_deleted", document_id=str(document_id))
        return True
    async def get_total_chunk_count(self,db:AsyncSession)-> int:
        stmt = select(func.count(Chunk.id))
        result = await db.execute(stmt)
        return result.scalar_one()
            