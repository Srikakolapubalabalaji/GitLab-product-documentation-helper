import pytest
from backend.app.services.ingestion.loader import load_documents_from_directory
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.services.vectorstore.faiss_store import get_vector_store
from backend.app.config.settings import settings

def test_faiss_vectorstore_build_and_search():
    docs = load_documents_from_directory(settings.DOCS_DIR)
    chunks = chunk_documents(docs)
    
    store = get_vector_store()
    count = store.build_index(chunks)
    assert count > 0
    assert store.count() == count

    # Perform similarity search
    results = store.similarity_search_with_score("How to register GitLab runner?", k=3)
    assert len(results) > 0
    best_doc, score = results[0]
    assert "runner" in best_doc.page_content.lower() or "gitlab" in best_doc.page_content.lower()
