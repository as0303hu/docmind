from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.pdf_parser import PDFParser
app = FastAPI(
    title="Docmind",
    description="Ask questions about your Pdf documentd using RAG",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {"status":"halthy","version":"0.1.0"}

@app.get("/debug/db/ping")
async def debug_db_ping(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
    except (SQLAlchemyError, OSError, ConnectionError) as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {exc}",
        ) from exc
    return {"status":"connected","result":result.scalar_one()}

@app.post("/debug/pdf/parse")
async def debug_parse_pdf(file: UploadFile = File(...)):
    content_type = (file.content_type or "").lower()
    if content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    pdf_bytes = await file.read()
    parser = PDFParser()

    try:
        pages = parser.extract_pages(pdf_bytes)
        page_count = parser.get_page_count(pdf_bytes)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "filename": file.filename,
        "page_count": page_count,
        "page_with_text": len(pages),
        "pages": [
            {
                "page_number": page.page_number,
                "text_preview": page.text[:300],
            }
            for page in pages
        ],
    }
    