from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from sqlalchemy import text

from app.api.v1.routes import documents, health, qa
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.middleware.correlation import CorrelationIdMiddleware



@asynccontextmanager
async def lifespan(app:FastAPI):
    setup_logging(settings.log_level)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    
app = FastAPI(
    title="Docmind",
    description="Ask questions about your Pdf documentd using RAG",
    version="0.1.0"
)
prefix = "/app/v1"
app.add_middleware(CorrelationIdMiddleware)

app.include_router(health.router,prefix=prefix)
app.include_router(documents.router,prefix=prefix)
app.include_router(qa.router,prefix=prefix)
 