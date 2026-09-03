from fastapi import FastAPI
app = FastAPI(
    title="Docmind",
    description="Ask questions about your Pdf documentd using RAG",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {"status":"halthy","version":"0.1.0"}