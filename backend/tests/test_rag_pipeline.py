import pytest
from backend.app.models.schemas import ChatRequest
from backend.app.services.ingestion.loader import load_documents_from_directory
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.services.vectorstore.faiss_store import get_vector_store
from backend.app.services.rag.pipeline import get_rag_pipeline
from backend.app.config.settings import settings

@pytest.fixture(autouse=True)
def setup_vector_index():
    store = get_vector_store()
    if store.count() == 0:
        docs = load_documents_from_directory(settings.DOCS_DIR)
        chunks = chunk_documents(docs)
        store.build_index(chunks)

def test_rag_pipeline_known_question():
    pipeline = get_rag_pipeline()
    req = ChatRequest(question="How do I create a merge request in GitLab?")
    res = pipeline.query(req)
    
    assert res is not None
    assert len(res.sources) > 0 or "Ollama Service" in res.answer or "ollama" in res.answer.lower()
    assert any("merge" in s.document_name.lower() or "merge" in s.section_name.lower() for s in res.sources)

def test_rag_pipeline_out_of_domain():
    pipeline = get_rag_pipeline()
    req = ChatRequest(question="What is the capital of France?")
    res = pipeline.query(req)
    
    # Should decline out-of-domain knowledge gracefully
    assert "couldn't find" in res.answer.lower() or "not found" in res.answer.lower() or "ollama" in res.answer.lower()
