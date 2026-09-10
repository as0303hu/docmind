"""Question-answering service that combines retreival with LLM generation."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.core.openai_client import get_openai_client, with_retry
from app.core.pii import redact_pii
from app.core.prompts import SYSTEM_PROMPT,USER_PROMPT_TEMPLATE
from app.models.schemas import AnswerResponse, SourceChunk
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore

logger = get_logger(__name__)


class QAService:
    """Orchestrates the RAG pipline: embed query -> retrieve chunks -> generate answer."""
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    def _build_context(self,search_results:list)->str:
        context_parts = []
        for chunk, score in search_results:
            context_parts.append(f"[Page {chunk.page_number}] {chunk.content}")
        return "\n\n---\n\n".join(context_parts)
    
    @with_retry()
    async def _generate_answer(self,question:str,context:str)-> str:
        """Call the LLM with PII-redacted content and retry on transient failures."""
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context = redact_pii(context),
            question = redact_pii(question)
        )
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":user_prompt},
            ], 
        )
        return response.choices[0].message.content

    async def ask(
        self,
        db: AsyncSession,
        question: str,
        top_k: int = settings.top_k,
    ) -> AnswerResponse:
        """Answer a question by searching stored document chunks."""
        query_embedding = await self.embedding_service.genrate_embedding(question)
        search_results = await self.vector_store.similarity_search(db, query_embedding, top_k=top_k)
        if not search_results:
            return AnswerResponse(
                question=question,
                answer="No documents uploaded yet, Please upload a Pdf first.",
                sources=[],
                model=settings.llm_model,
                total_chunks_searched=0,
            )

        context = self._build_context(search_results)
        answer = await self._generate_answer(question,context)
        
        sources = [
            SourceChunk(
                content=chunk.content[:300],
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                similarity_score=round(score, 4),
            )
            for chunk, score in search_results
        ]
        total_chunks = await self.vector_store.get_total_chunk_count(db)

        logger.info(
            "question_answered",
            question_length=len(question),
            sources_used=len(sources),
            total_chunks_searched = total_chunks
        )

        return AnswerResponse(
            question=question,
            answer=answer,
            sources=sources,
            model=settings.llm_model,
            total_chunks_searched=total_chunks,
        )
