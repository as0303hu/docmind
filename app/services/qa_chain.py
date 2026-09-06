from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.openai import chat_model_name,create_openai_client
from app.models.schemas import AnswerResponse, SourceChunk
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore

logger = get_logger(__name__)

client = create_openai_client()

SYSTEM_PROMPT = """ You are a helpful assistant that answers questions based on the provided context from PDF documents.
RUles:
- only answer based on the provided context. Do not use prior Knowledge.
-If the context doesn't contain enough information, say so  clearly.
- Reference which page the information comes from.
- Be concise and direct.
"""
USER_PROMPT_TEMPLATE = """COntext from documents:
{context}
Question: {question}
Answer based only on the context above. Reference page numbers when possible.
"""

class QAService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    async def ask(
    self,
    db:AsyncSession,
    question: str,
    top_k:int = settings.top_k,
    )->AnswerResponse:
        query_embedding = await self.embedding_service.genrate_embedding(question)
        search_results = await self.vector_store.similarity_search(
            db,query_embedding,top_k=top_k
        )
        if not search_results:
            return AnswerResponse(
                question=question,
                answer="No documents uploaded yet, Please upload a Pdf first.",
                sources=[],
                model=settings.llm_model,
                total_chunks_searched=0
            )
        
        context_parts = []
        for chunk,score in search_results:
            context_parts.append(f"[Page {chunk.page_number}] {chunk.content}")
        context = "\n\n ---\n\n".join(context_parts)
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context = context, question = question
        )
        response = await client.chat.completions.create(
            model=chat_model_name(),
            temperature= settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":user_prompt}
            ],
        )
        answer = response.choices[0].message.content
        sources = [
            SourceChunk(
                content= chunk.content[:300],
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                similarity_score=round(score,4),
            )
            for chunk,score in search_results
        ]
        total_chunks = await self.vector_store.get_total_chunk_count(db)
        
        logger.info(
            "question_answered",
            question_length = len(question),
            sources_used = len(sources),
        )
        
        return AnswerResponse(
            question=question,
            answer=answer,
            sources=sources,
            model=settings.llm_model,
            total_chunks_searched=total_chunks
        )