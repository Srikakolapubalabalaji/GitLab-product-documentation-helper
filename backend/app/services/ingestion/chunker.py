import uuid
import re
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.app.config.settings import settings

def find_doc_title(full_text: str) -> str:
    """Extracts the top-level H1 title from document text if present."""
    match = re.search(r'^#\s+(.+)$', full_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""

def find_section_header_for_chunk(full_text: str, chunk_text: str) -> str:
    """Finds the most relevant Markdown section header preceding or contained within the chunk."""
    match = re.search(r'^(?:#{1,4})\s+(.+)$', chunk_text, re.MULTILINE)
    if match:
        return match.group(1).strip()

    chunk_pos = full_text.find(chunk_text)
    if chunk_pos != -1:
        prior_text = full_text[:chunk_pos]
        headers = re.findall(r'^(?:#{1,4})\s+(.+)$', prior_text, re.MULTILINE)
        if headers:
            return headers[-1].strip()

    return "General"

def chunk_documents(
    documents: List[Document],
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP
) -> List[Document]:
    """
    Splits documents into smaller meaningful chunks while preserving section headers, code blocks,
    contextual metadata, and domain provenance.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n## ",      # H2 headers
            "\n### ",     # H3 headers
            "\n#### ",    # H4 headers
            "```\n",      # Code blocks
            "\n\n",       # Paragraphs
            "\n- ",       # Bullet lists
            "\n",         # Lines
            " ",          # Words
            ""
        ]
    )
    
    chunked_docs: List[Document] = []
    
    for doc in documents:
        full_text = doc.page_content
        doc_title = find_doc_title(full_text) or doc.metadata.get("document_name", "GitLab Documentation")
        
        raw_chunks = splitter.split_documents([doc])
        for idx, chunk in enumerate(raw_chunks):
            doc_name = doc.metadata.get('document_name', 'doc')
            chunk_id = f"{doc_name}_chunk_{idx}_{uuid.uuid4().hex[:6]}"
            
            section_name = find_section_header_for_chunk(full_text, chunk.page_content)
            if section_name == "General" and "section_name" in doc.metadata and doc.metadata["section_name"] != "General":
                section_name = doc.metadata["section_name"]
                
            updated_metadata = dict(doc.metadata)
            updated_metadata.update({
                "chunk_id": chunk_id,
                "chunk_index": idx,
                "section_name": section_name,
                "doc_title": doc_title
            })
            
            content_str = chunk.page_content.strip()
            # If chunk does not already start with a top header, prepend context header for embedding accuracy
            if not content_str.startswith("# ") and not content_str.startswith("Document Context:"):
                context_prefix = f"Document: {doc_title} | Section: {section_name}\n"
                if not content_str.startswith(context_prefix):
                    content_str = f"{context_prefix}{content_str}"
            
            chunked_doc = Document(
                page_content=content_str,
                metadata=updated_metadata
            )
            chunked_docs.append(chunked_doc)
            
    return chunked_docs
