import os
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "-1")

import re
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from backend.app.services.ingestion.cleaner import clean_text



def extract_source_url(content: str) -> str:
    """Extract Source URL header if present in document text."""
    match = re.search(r'Source URL:\s*(https?://[^\s\n]+)', content, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def load_single_document(file_path: str) -> List[Document]:
    """
    Loads a single document file (.md, .txt, .pdf, .html) and returns a list of LangChain Document objects
    with rich metadata.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = path.suffix.lower()
    doc_name = path.name
    doc_type = file_ext.lstrip(".")
    
    documents: List[Document] = []
    
    if file_ext in [".md", ".txt"]:
        loader = TextLoader(file_path, encoding="utf-8")
        raw_docs = loader.load()
        for doc in raw_docs:
            cleaned_content = clean_text(doc.page_content)
            source_url = extract_source_url(cleaned_content) or f"https://docs.gitlab.com/ee/{path.stem}"
            doc.page_content = cleaned_content
            doc.metadata.update({
                "document_name": doc_name,
                "source_url": source_url,
                "document_type": doc_type,
                "file_path": str(path.resolve()),
                "section_name": "General"
            })
            documents.append(doc)
            
    elif file_ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        raw_docs = loader.load()
        for doc in raw_docs:
            cleaned_content = clean_text(doc.page_content)
            page_num = doc.metadata.get("page", 0) + 1
            doc.page_content = cleaned_content
            doc.metadata.update({
                "document_name": doc_name,
                "source_url": f"https://docs.gitlab.com/ee/pdf/{doc_name}#page={page_num}",
                "page_number": page_num,
                "document_type": doc_type,
                "file_path": str(path.resolve()),
                "section_name": f"Page {page_num}"
            })
            documents.append(doc)
            
    elif file_ext in [".html", ".htm"]:
        try:
            from langchain_community.document_loaders import UnstructuredHTMLLoader
            loader = UnstructuredHTMLLoader(file_path)
            raw_docs = loader.load()
        except Exception:
            loader = TextLoader(file_path, encoding="utf-8")
            raw_docs = loader.load()

            
        for doc in raw_docs:
            cleaned_content = clean_text(doc.page_content)
            source_url = extract_source_url(cleaned_content) or f"https://docs.gitlab.com/ee/{path.stem}"
            doc.page_content = cleaned_content
            doc.metadata.update({
                "document_name": doc_name,
                "source_url": source_url,
                "document_type": doc_type,
                "file_path": str(path.resolve()),
                "section_name": "Web Documentation"
            })
            documents.append(doc)
    else:
        raise ValueError(f"Unsupported document format: {file_ext}")
        
    return documents

def load_documents_from_directory(directory_path: str) -> List[Document]:
    """
    Scans directory for supported document files and loads all of them.
    """
    dir_path = Path(directory_path)
    if not dir_path.exists():
        return []
        
    all_documents: List[Document] = []
    supported_extensions = [".md", ".txt", ".pdf", ".html", ".htm"]
    
    for file in dir_path.rglob("*"):
        if file.is_file() and file.suffix.lower() in supported_extensions:
            try:
                docs = load_single_document(str(file))
                all_documents.extend(docs)
            except Exception as e:
                print(f"Error loading document {file.name}: {e}")
                
    return all_documents
