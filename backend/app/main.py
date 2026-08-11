import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config.settings import settings
from backend.app.api import chat, documents, evaluation, health
from backend.app.services.ingestion.loader import load_documents_from_directory
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.services.vectorstore.faiss_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gitlab_rag_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing GitLab Documentation Helper Backend...")
    vector_store = get_vector_store()
    
    docs_dir = Path(settings.DOCS_DIR)
    if docs_dir.exists():
        raw_docs = load_documents_from_directory(str(docs_dir))
        chunks = chunk_documents(raw_docs) if raw_docs else []
        
        current_vec_count = vector_store.count()
        fresh_chunk_count = len(chunks)
        
        # Always rebuild if mismatch between stored index and fresh corpus count
        if current_vec_count == 0 or current_vec_count != fresh_chunk_count:
            logger.info(
                f"Rebuilding FAISS index: {len(raw_docs)} docs → {fresh_chunk_count} chunks "
                f"(stored: {current_vec_count}). This may take a moment..."
            )
            vector_store.build_index(chunks)
            logger.info(f"✓ FAISS index ready: {vector_store.count()} vectors indexed from {len(raw_docs)} documents.")
        else:
            logger.info(f"✓ Loaded FAISS index: {current_vec_count} vectors from {len(raw_docs)} document files.")
    else:
        logger.warning("No sample documents directory found. FAISS index will be empty.")
        
    yield
    logger.info("Shutting down GitLab Documentation Helper Backend...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-style RAG API for GitLab Product Documentation powered by FastAPI, FAISS, and Ollama LLM.",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    settings.FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(evaluation.router, prefix=settings.API_V1_STR)
app.include_router(health.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GitLab Product Documentation Helper API",
        "health_check": f"{settings.API_V1_STR}/health",
        "docs": "/docs"
    }
