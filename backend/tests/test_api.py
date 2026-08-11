import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "vector_count" in data

def test_documents_list_endpoint():
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert data["total_documents"] > 0

def test_chat_endpoint():
    response = client.post("/api/chat", json={"question": "What is a GitLab Runner?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
