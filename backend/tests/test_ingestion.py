import pytest
from pathlib import Path
from backend.app.services.ingestion.loader import load_documents_from_directory, load_single_document
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.config.settings import settings

def test_load_documents_from_directory():
    docs = load_documents_from_directory(settings.DOCS_DIR)
    assert len(docs) > 0
    assert any("gitlab" in doc.metadata.get("document_name", "").lower() for doc in docs)

def test_chunking_preserves_metadata():
    docs = load_documents_from_directory(settings.DOCS_DIR)
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
    assert len(chunks) >= len(docs)
    
    first_chunk = chunks[0]
    assert "document_name" in first_chunk.metadata
    assert "chunk_id" in first_chunk.metadata
    assert "source_url" in first_chunk.metadata
    assert len(first_chunk.page_content) > 0
