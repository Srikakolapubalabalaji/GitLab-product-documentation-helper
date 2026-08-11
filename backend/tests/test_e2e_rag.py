import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config.settings import settings
from backend.app.services.ingestion.loader import load_documents_from_directory
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.services.embeddings.embedding_service import get_embedding_service
from backend.app.services.vectorstore.faiss_store import get_vector_store
from backend.app.services.rag.retriever import DocumentRetriever
from backend.app.services.rag.pipeline import get_rag_pipeline, format_conversation_history
from backend.app.models.schemas import ChatRequest, ChatMessage

client = TestClient(app)

# ---------------------------------------------------------
# 1. APPLICATION STARTUP & API ENDPOINTS
# ---------------------------------------------------------
def test_startup_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["vector_count"] >= 0
    assert "embedding_model" in data

def test_documents_list_endpoint():
    res = client.get("/api/documents")
    assert res.status_code == 200
    data = res.json()
    assert data["total_documents"] >= 7
    assert data["total_chunks"] > 0
    assert len(data["documents"]) > 0

# ---------------------------------------------------------
# 2. DOCUMENT INGESTION & CHUNKING
# ---------------------------------------------------------
def test_ingestion_data_validity():
    """All documents must load with non-empty content and proper metadata."""
    docs = load_documents_from_directory(settings.DOCS_DIR)
    assert len(docs) > 0
    for doc in docs:
        assert len(doc.page_content.strip()) > 0
        assert "document_name" in doc.metadata
        assert "source_url" in doc.metadata

def test_chunking_non_empty_and_metadata():
    """All chunks must have non-empty content, a chunk_id, doc name, and section name."""
    docs = load_documents_from_directory(settings.DOCS_DIR)
    chunks = chunk_documents(docs, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    assert len(chunks) >= len(docs)
    for chunk in chunks:
        assert len(chunk.page_content.strip()) > 0, "Chunk content must not be empty"
        assert "chunk_id" in chunk.metadata
        assert "document_name" in chunk.metadata
        assert "section_name" in chunk.metadata
        assert "doc_title" in chunk.metadata

def test_chunk_context_prefix_injected():
    """Chunks should contain 'Document:' prefix for better embedding context."""
    docs = load_documents_from_directory(settings.DOCS_DIR)
    chunks = chunk_documents(docs, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    has_prefix = any("Document:" in chunk.page_content for chunk in chunks)
    assert has_prefix, "At least some chunks should have a 'Document:' context prefix injected"

# ---------------------------------------------------------
# 3. EMBEDDINGS
# ---------------------------------------------------------
def test_embedding_service_consistency():
    """Embedding dimensions must be consistent between doc and query embedders."""
    service = get_embedding_service()
    doc_vec = service.embed_documents(["GitLab Project management"])[0]
    query_vec = service.embed_query("GitLab Project management")
    assert len(doc_vec) == len(query_vec)
    assert isinstance(query_vec[0], float)

# ---------------------------------------------------------
# 4. FAISS VECTORSTORE PERSISTENCE
# ---------------------------------------------------------
def test_vectorstore_persistence_and_reload():
    store = get_vector_store()
    initial_count = store.count()
    assert initial_count > 0, "FAISS index should contain vectors"
    
    index_dir = Path(settings.VECTORSTORE_DIR) / "faiss_index"
    assert (index_dir / "index.faiss").exists()
    assert (index_dir / "index.pkl").exists()

    loaded_success = store.load_index()
    assert loaded_success is True
    assert store.count() == initial_count

# ---------------------------------------------------------
# 5. RETRIEVAL – MULTI-TOPIC COVERAGE (General Purpose)
# ---------------------------------------------------------
@pytest.mark.parametrize("query,expected_keyword", [
    # Core concepts
    ("What is GitLab?", "gitlab"),
    ("How do I create a GitLab project?", "project"),
    # CI/CD
    ("What is GitLab CI/CD?", "pipeline"),
    ("What is a GitLab CI/CD pipeline stage?", "stage"),
    ("How do rules work in .gitlab-ci.yml?", "rules"),
    ("What are parent-child pipelines?", "trigger"),
    # Runners
    ("What is a GitLab Runner?", "runner"),
    ("What GitLab runner executor types are available?", "executor"),
    # Merge Requests
    ("How do I create a merge request?", "merge"),
    ("What are draft merge requests?", "draft"),
    ("What are GitLab merge strategies?", "squash"),
    # Auth & Tokens
    ("How does GitLab authentication work?", "token"),
    ("What is a Personal Access Token?", "personal access token"),
    ("What is a Deploy Token in GitLab?", "deploy"),
    ("What is CI_JOB_TOKEN?", "ci_job_token"),
    # Security
    ("What is SAST in GitLab security?", "sast"),
    ("What does Container Scanning do?", "container scanning"),
    ("What is Secret Detection in GitLab?", "secret detection"),
    # Comparisons
    ("What is the difference between Personal Access Tokens and Deploy Tokens?", "deploy"),
    ("What is the difference between Cache and Artifacts in GitLab CI/CD?", "cache"),
    # Branch Protection & CODEOWNERS
    ("How do I configure protected branches?", "protect"),
    ("How does the CODEOWNERS file work in GitLab?", "codeowners"),
    # Container/Package Registry
    ("How do I push container images to GitLab Container Registry?", "registry"),
    # Troubleshooting
    ("Why is my GitLab CI job stuck?", "runner"),
    # Administration
    ("Where are Gitaly logs located for troubleshooting?", "gitaly"),
])
def test_retrieval_core_questions(query, expected_keyword):
    """Retrieval must return chunks for all major GitLab topics and keyword domains."""
    retriever = DocumentRetriever(top_k=settings.TOP_K)
    raw_results, sources, retrieved_chunks_dto = retriever.retrieve(query)
    
    assert len(retrieved_chunks_dto) > 0, f"Retrieval failed for query: '{query}'"
    assert len(retrieved_chunks_dto) <= settings.TOP_K, "TOP_K limit exceeded"
    
    combined_content = " ".join([c.content.lower() for c in retrieved_chunks_dto])
    assert expected_keyword in combined_content, (
        f"Keyword '{expected_keyword}' missing in retrieved chunks for '{query}'"
    )

# ---------------------------------------------------------
# 6. RAG GROUNDING & OUT-OF-SCOPE REJECTION
# ---------------------------------------------------------
@pytest.mark.parametrize("out_of_scope_query", [
    "What is the capital of France?",
    "How do I cook biryani?",
    "Tell me today's weather.",
    "Who is the CEO of Apple?",
])
def test_out_of_scope_questions(out_of_scope_query):
    """Out-of-domain questions must return fallback phrase or Ollama unavailable message."""
    pipeline = get_rag_pipeline()
    req = ChatRequest(question=out_of_scope_query)
    res = pipeline.query(req)
    
    fallback_phrase = "couldn't find this information in the available gitlab documentation"
    answer_lower = res.answer.lower()
    
    assert fallback_phrase in answer_lower or "ollama service unavailable" in answer_lower, (
        f"Expected fallback for out-of-scope query '{out_of_scope_query}' but got: {res.answer[:150]}"
    )

# ---------------------------------------------------------
# 7. SOURCE CITATIONS
# ---------------------------------------------------------
def test_source_citations_structure():
    """Sources must have non-empty names, valid URLs, and non-negative scores."""
    retriever = DocumentRetriever(top_k=3)
    _, sources, _ = retriever.retrieve("How do I configure gitlab runner?")
    assert len(sources) > 0
    for source in sources:
        assert source.document_name != ""
        url = source.source_url or ""
        assert url == "" or url.startswith("http://") or url.startswith("https://")
        assert source.score >= 0.0

def test_source_citations_deduplicated():
    """Each (document_name, section_name) combination should appear at most once in sources."""
    retriever = DocumentRetriever(top_k=settings.TOP_K)
    _, sources, _ = retriever.retrieve("What is CI/CD?")
    source_keys = [(s.document_name, s.section_name) for s in sources]
    assert len(source_keys) == len(set(source_keys)), "Duplicate source citations found"

# ---------------------------------------------------------
# 8. CONVERSATIONAL MULTI-TURN RAG
# ---------------------------------------------------------
def test_conversational_history_formatting():
    history = [
        ChatMessage(role="user", content="What is GitLab CI/CD?"),
        ChatMessage(role="assistant", content="GitLab CI/CD is a tool for continuous integration and delivery.")
    ]
    formatted = format_conversation_history(history)
    assert "User: What is GitLab CI/CD?" in formatted
    assert "Assistant: GitLab CI/CD is a tool" in formatted

def test_conversation_history_truncated_to_last_4():
    """Only the last 4 messages should appear in formatted history."""
    history = [
        ChatMessage(role="user", content=f"Message {i}") for i in range(8)
    ]
    formatted = format_conversation_history(history)
    assert "Message 0" not in formatted, "History older than 4 turns should be truncated"
    assert "Message 7" in formatted

# ---------------------------------------------------------
# 9. ERROR HANDLING & SECURITY
# ---------------------------------------------------------
def test_chat_empty_question():
    res = client.post("/api/chat", json={"question": "   "})
    assert res.status_code in [422, 200]
    if res.status_code == 200:
        data = res.json()
        assert "valid" in data["answer"].lower() or "empty" in data["answer"].lower()

def test_chat_very_long_question():
    long_q = "How do I create a GitLab project? " * 100
    res = client.post("/api/chat", json={"question": long_q})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data

def test_security_env_file_ignored():
    gitignore_path = Path(settings.VECTORSTORE_DIR).parent.parent / ".gitignore"
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        assert ".env" in content

# ---------------------------------------------------------
# 10. EVALUATION ENDPOINT
# ---------------------------------------------------------
def test_evaluation_endpoint():
    res = client.post("/api/evaluate")
    assert res.status_code == 200
    data = res.json()
    assert "grounded_rate_pct" in data
    assert "avg_latency_sec" in data
    assert data["total_questions"] > 0
