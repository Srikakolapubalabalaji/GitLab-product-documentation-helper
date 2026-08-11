from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of speaker: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question about GitLab")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous dialogue turns")

class SourceMetadata(BaseModel):
    document_name: str
    section_name: Optional[str] = "General"
    page_number: Optional[int] = None
    source_url: Optional[str] = None
    document_type: str = "markdown"
    score: float = 0.0
    chunk_snippet: str = ""

class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata] = []
    retrieved_chunks: List[RetrievedChunk] = []
    conversation_id: Optional[str] = None
    error: Optional[str] = None

class IngestResponse(BaseModel):
    message: str
    documents_processed: int
    total_chunks: int
    total_vectors: int

class DocumentItem(BaseModel):
    document_name: str
    chunk_count: int
    file_size_bytes: int
    source_url: Optional[str] = None
    document_type: str

class DocumentListResponse(BaseModel):
    total_documents: int
    total_chunks: int
    documents: List[DocumentItem]

class EvalQuestion(BaseModel):
    id: str
    question: str
    expected_topics: List[str]
    category: str  # e.g., 'Core Concepts', 'CI/CD', 'Auth', 'Out of Domain'

class EvalResultItem(BaseModel):
    question_id: str
    question: str
    category: str
    retrieved_chunks_count: int
    answer_snippet: str
    sources: List[str]
    is_grounded: bool
    relevance_score: float
    execution_time_sec: float

class EvalResponse(BaseModel):
    timestamp: str
    total_questions: int
    avg_latency_sec: float
    grounded_rate_pct: float
    results: List[EvalResultItem]
