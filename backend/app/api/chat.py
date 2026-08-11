from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.services.rag.pipeline import get_rag_pipeline

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    RAG Chat endpoint for querying GitLab Product Documentation.
    Accepts question and optional dialogue history.
    """
    try:
        pipeline = get_rag_pipeline()
        response = pipeline.query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat query: {str(e)}")
