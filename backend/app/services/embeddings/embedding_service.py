import os
import logging
from typing import List, Optional

# Ensure torch uses CPU safely without CUDA DLL loading issues on Windows
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

from langchain_core.embeddings import Embeddings
from backend.app.config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _embeddings: Optional[Embeddings] = None
    provider_name: str = "unknown"

    def __init__(self, provider: str = settings.EMBEDDING_PROVIDER, model_name: str = settings.EMBEDDING_MODEL):
        self.provider = provider
        self.model_name = model_name
        self._init_model()

    def _init_model(self):
        # Hugging Face Local Embeddings
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            logger.info(f"Initializing HuggingFaceEmbeddings with model: {self.model_name}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            self.provider_name = f"huggingface ({self.model_name})"
        except Exception as e:
            logger.warning(f"Failed to load via langchain_huggingface, falling back to langchain_community: {e}")
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=self.model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                self.provider_name = f"huggingface ({self.model_name})"
            except Exception as ex:
                logger.error(f"Critical error initializing embedding model: {ex}")
                raise RuntimeError(f"Could not initialize HuggingFace embeddings: {ex}")

    @property
    def embeddings(self) -> Embeddings:
        if self._embeddings is None:
            self._init_model()
        return self._embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

def get_embedding_service() -> EmbeddingService:
    if EmbeddingService._instance is None:
        EmbeddingService._instance = EmbeddingService()
    return EmbeddingService._instance

