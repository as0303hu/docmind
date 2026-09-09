from contextlib import asynccontextmanager
from fastapi import  FastAPI
from sqlalchemy import text

from app.api.v1.routes import documents, health, qa
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.middleware.correlation import CorrelationIdMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.error_handler import register_error_handlers



@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)
    yield
    await engine.dispose()
    
app = FastAPI(
    title="Docmind",
    description="Ask questions about your Pdf documentd using RAG",
    version="0.1.0",
    lifespan=lifespan,
)
prefix = "/api/v1"
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)

app.include_router(health.router,prefix=prefix)
app.include_router(documents.router,prefix=prefix)
app.include_router(qa.router,prefix=prefix)
 
register_error_handlers(app)