from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import EvalResponse
from backend.app.services.evaluation.evaluator import get_rag_evaluator

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])

@router.post("", response_model=EvalResponse)
async def evaluate_rag():
    """
    Runs automated benchmark RAG quality evaluation.
    Measures groundedness rate, average retrieval latency, and context relevance scores.
    """
    try:
        evaluator = get_rag_evaluator()
        report = evaluator.run_evaluation()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute RAG evaluation: {str(e)}")
