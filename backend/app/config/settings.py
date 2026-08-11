import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "GitLab Product Documentation Helper"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Ollama LLM Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_NAME: str = "llama3.2:1b"
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: str = "huggingface"  # 100% local embedding model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # RAG Retrieval Configuration
    TOP_K: int = 4                       # Optimal 3-5 range for fast context processing
    SIMILARITY_THRESHOLD: float = 0.20   # Balanced similarity filter for technical accuracy
    CHUNK_SIZE: int = 1000               # Larger chunks preserve code blocks & multi-step instructions
    CHUNK_OVERLAP: int = 200             # Higher overlap keeps contextual continuity across splits
    
    # Paths
    VECTORSTORE_DIR: str = str(BASE_DIR / "backend" / "vectorstore_db")
    DOCS_DIR: str = str(BASE_DIR / "backend" / "data" / "sample_docs")
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
