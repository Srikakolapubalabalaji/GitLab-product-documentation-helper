import pytest
from backend.app.services.embeddings.embedding_service import get_embedding_service

def test_embedding_service_query():
    service = get_embedding_service()
    vec = service.embed_query("How do I create a GitLab project?")
    assert isinstance(vec, list)
    assert len(vec) > 0
    assert isinstance(vec[0], float)

def test_embedding_service_batch():
    service = get_embedding_service()
    vecs = service.embed_documents(["GitLab CI/CD", "Merge Request"])
    assert len(vecs) == 2
    assert len(vecs[0]) == len(vecs[1])
