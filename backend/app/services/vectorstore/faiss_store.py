import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from backend.app.config.settings import settings
from backend.app.services.embeddings.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

INDEX_FOLDER_NAME = "faiss_index"

class FAISSVectorStore:
    def __init__(self, persistence_dir: str = settings.VECTORSTORE_DIR):
        self.persistence_dir = Path(persistence_dir)
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_service = get_embedding_service()
        self.vector_store: Optional[FAISS] = None
        self.load_index()

    def index_exists(self) -> bool:
        """Checks if a saved FAISS index exists on disk."""
        index_file = self.persistence_dir / INDEX_FOLDER_NAME / "index.faiss"
        pkl_file = self.persistence_dir / INDEX_FOLDER_NAME / "index.pkl"
        return index_file.exists() and pkl_file.exists()

    def load_index(self) -> bool:
        """Loads index from local disk if present."""
        if self.index_exists():
            try:
                save_path = str(self.persistence_dir / INDEX_FOLDER_NAME)
                logger.info(f"Loading existing FAISS index from {save_path}...")
                self.vector_store = FAISS.load_local(
                    save_path,
                    self.embedding_service.embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info("FAISS index loaded successfully.")
                return True
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                self.vector_store = None
                return False
        else:
            logger.info("No existing FAISS index found on disk.")
            self.vector_store = None
            return False

    def build_index(self, documents: List[Document]) -> int:
        """
        Creates FAISS index from documents and saves it to local disk.
        """
        if not documents:
            logger.warning("No documents provided for indexing.")
            return 0

        logger.info(f"Creating FAISS vector store with {len(documents)} chunks...")
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embedding_service.embeddings
        )
        self.save_index()
        return len(documents)

    def save_index(self):
        """Saves current FAISS index to local disk."""
        if self.vector_store:
            save_path = str(self.persistence_dir / INDEX_FOLDER_NAME)
            logger.info(f"Saving FAISS index to {save_path}...")
            self.vector_store.save_local(save_path)
            logger.info("FAISS index saved successfully.")

    def similarity_search_with_score(
        self,
        query: str,
        k: int = settings.TOP_K
    ) -> List[Tuple[Document, float]]:
        """
        Searches FAISS for top-k similar documents given a query string.
        Returns list of (Document, score) tuples.
        """
        if not self.vector_store:
            if not self.load_index():
                logger.warning("FAISS vector store is not initialized or index missing.")
                return []
                
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error during similarity search (dimension mismatch or index error): {e}")
            return []

    def count(self) -> int:
        """Returns total number of vectors in index."""
        if self.vector_store and hasattr(self.vector_store, "index"):
            return self.vector_store.index.ntotal
        return 0

# Singleton instance for application access
_faiss_store_instance: Optional[FAISSVectorStore] = None

def get_vector_store() -> FAISSVectorStore:
    global _faiss_store_instance
    if _faiss_store_instance is None:
        _faiss_store_instance = FAISSVectorStore()
    return _faiss_store_instance
