from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.dependencies import get_qa_service
from app.models.schemas import AnswerResponse,QuestionRequest

router =APIRouter(prefix="/qa",tags=["question-answering"])

@router.post("/ask",response_model=AnswerResponse)
async def ask_quesiton(
    request:QuestionRequest,
    db:AsyncSession = Depends(get_db),
    qa_service = Depends(get_qa_service),
):
    return await qa_service.ask(
        db=db,
        question=request.question,
        top_k=request.top_k,
    )