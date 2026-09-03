import uuid
from datetime import datetime

from pydantic import BaseModel, Field

class DocumentUploadResponse(BaseModel):
    id:uuid.UUID
    filename:str
    file_size:int
    page_count:int
    chunk_count:int
    created_at:datetime
    
    model_config = {"from_attributes":True}

class DocumentListItem(BaseModel):
    id: uuid.UUID
    filename: str
    page_count: int
    chunk_count: int
    created_at: datetime
    
    model_config={"from_attributes":True}
    
class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]
    total_count:int

class QuestionRequest(BaseModel):
    question:str =Field(...,min_length=3,max_length=1000)
    top_k:int = Field(default=5,ge=1, le=20)

class SourceChunk(BaseModel):
    content: str
    page_number:int
    chunk_index:int
    similarity_score:float
    
class AnswerResponse(BaseModel):
    question:str
    answer:str
    sources:list[SourceChunk]
    model:str
    total_chunks_searched:int

class HealthResponse(BaseModel):
    status:str
    database:str
    version:str="1.0.0"
    