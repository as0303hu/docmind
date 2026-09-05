from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import async_session_factory
from app.models.schemas import HealthResponse

router = APIRouter()

@router.get("/health",response_model=HealthResponse)
async def health_check():
    db_status = "Helathy"
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"
    
    return HealthResponse(
        status="healthy",
        database=db_status
    )

    