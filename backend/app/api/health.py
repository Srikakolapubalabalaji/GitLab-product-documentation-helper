from fastapi import APIRouter
from backend.app.config.settings import settings
from backend.app.services.vectorstore.faiss_store import get_vector_store
from backend.app.services.embeddings.embedding_service import get_embedding_service
from backend.app.services.llm.ollama_service import get_ollama_service

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def health_check():
    """
    Returns system status, active vector index vector count, embedding model name,
    and local Ollama service readiness state.
    """
    vector_store = get_vector_store()
    ollama = get_ollama_service()
    embedding_service = get_embedding_service()

    ollama_ready = ollama.is_service_available()
    ollama_model_ready = ollama.is_model_available() if ollama_ready else False

    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "embedding_model": embedding_service.provider_name,
        "vector_count": vector_store.count(),
        "vector_index_ready": vector_store.count() > 0,
        "ollama_service_ready": ollama_ready,
        "ollama_model_ready": ollama_model_ready,
        "ollama_model": settings.OLLAMA_MODEL_NAME,
        "ollama_base_url": settings.OLLAMA_BASE_URL
    }
