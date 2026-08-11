import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.config.settings import settings
from backend.app.models.schemas import IngestResponse, DocumentListResponse, DocumentItem
from backend.app.services.ingestion.loader import load_documents_from_directory, load_single_document
from backend.app.services.ingestion.chunker import chunk_documents
from backend.app.services.vectorstore.faiss_store import get_vector_store

router = APIRouter(prefix="", tags=["Documents"])

@router.post("/reindex", response_model=IngestResponse)
async def reindex_documents():
    """
    Re-scans documents directory, extracts text, chunks text, generates embeddings,
    and updates the FAISS vector database.
    """
    try:
        docs_dir = Path(settings.DOCS_DIR)
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        raw_documents = load_documents_from_directory(str(docs_dir))
        if not raw_documents:
            return IngestResponse(
                message="No document files found in storage directory.",
                documents_processed=0,
                total_chunks=0,
                total_vectors=0
            )

        chunks = chunk_documents(raw_documents)
        vector_store = get_vector_store()
        total_vectors = vector_store.build_index(chunks)

        return IngestResponse(
            message="Successfully re-indexed documentation database.",
            documents_processed=len(raw_documents),
            total_chunks=len(chunks),
            total_vectors=total_vectors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to re-index documents: {str(e)}")

@router.post("/ingest", response_model=IngestResponse)
async def upload_and_ingest(file: UploadFile = File(...)):
    """
    Uploads a document file (.md, .txt, .pdf, .html) and adds it to the RAG vector index.
    """
    allowed_exts = {".md", ".txt", ".pdf", ".html", ".htm"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(allowed_exts)}"
        )

    try:
        docs_dir = Path(settings.DOCS_DIR)
        docs_dir.mkdir(parents=True, exist_ok=True)
        save_path = docs_dir / file.filename

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Trigger reindex
        raw_documents = load_documents_from_directory(str(docs_dir))
        chunks = chunk_documents(raw_documents)
        vector_store = get_vector_store()
        total_vectors = vector_store.build_index(chunks)

        return IngestResponse(
            message=f"Document '{file.filename}' uploaded and indexed successfully.",
            documents_processed=len(raw_documents),
            total_chunks=len(chunks),
            total_vectors=total_vectors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest uploaded document: {str(e)}")

@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    Lists all indexed GitLab documentation files and current vector store statistics.
    """
    docs_dir = Path(settings.DOCS_DIR)
    doc_items: List[DocumentItem] = []
    total_chunks = 0
    vector_store = get_vector_store()

    if docs_dir.exists():
        for file in docs_dir.rglob("*"):
            if file.is_file() and file.suffix.lower() in [".md", ".txt", ".pdf", ".html", ".htm"]:
                try:
                    docs = load_single_document(str(file))
                    chunks = chunk_documents(docs)
                    chunk_count = len(chunks)
                    total_chunks += chunk_count
                    
                    doc_items.append(
                        DocumentItem(
                            document_name=file.name,
                            chunk_count=chunk_count,
                            file_size_bytes=file.stat().st_size,
                            source_url=docs[0].metadata.get("source_url") if docs else None,
                            document_type=file.suffix.lstrip(".")
                        )
                    )
                except Exception:
                    continue

    return DocumentListResponse(
        total_documents=len(doc_items),
        total_chunks=vector_store.count(),
        documents=doc_items
    )
