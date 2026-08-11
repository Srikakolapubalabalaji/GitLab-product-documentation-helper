import logging
import re
from typing import List, Tuple, Dict, Any
from langchain_core.documents import Document
from backend.app.config.settings import settings
from backend.app.services.vectorstore.faiss_store import get_vector_store
from backend.app.models.schemas import SourceMetadata, RetrievedChunk

logger = logging.getLogger(__name__)

STOPWORDS = {
    "what", "how", "why", "where", "when", "who", "which", "does", "do", "is",
    "are", "was", "were", "the", "a", "an", "and", "or", "in", "on", "of", "to",
    "for", "with", "can", "i", "you", "my", "by", "from", "it", "its", "this",
    "that", "these", "those", "about", "tell", "explain", "give", "me"
}

def extract_query_terms(text: str) -> set:
    """Extracts meaningful technical terms and keywords from query string."""
    raw_words = re.findall(r'[a-zA-Z0-9_\-\./]{2,}', text.lower())
    clean_words = {w.strip('.,()[]{}"\'') for w in raw_words}
    return {w for w in clean_words if w and w not in STOPWORDS}

def compute_keyword_match_ratio(query: str, text: str) -> float:
    """Computes keyword match density ratio for query terms in target text."""
    query_terms = extract_query_terms(query)
    if not query_terms:
        return 0.0
    text_lower = text.lower()
    matches = sum(1 for term in query_terms if term in text_lower)
    return matches / len(query_terms)

def build_expanded_query(query: str) -> str:
    """Expands short topic/keyword queries into richer semantic vectors for FAISS retrieval."""
    terms = extract_query_terms(query)
    # If query is short (4 words or fewer), construct semantic expansion
    word_count = len(query.strip().split())
    if word_count <= 4:
        topic_str = " ".join(terms) if terms else query
        return f"{query} {topic_str} overview definition architecture configuration guide setup"
    return query

class DocumentRetriever:
    def __init__(self, top_k: int = settings.TOP_K, similarity_threshold: float = settings.SIMILARITY_THRESHOLD):
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.vector_store = get_vector_store()

    def retrieve(self, query: str) -> Tuple[List[Tuple[Document, float]], List[SourceMetadata], List[RetrievedChunk]]:
        """
        Retrieves relevant chunks from FAISS vector database for query,
        applies multi-query expansion, hybrid vector + keyword match re-ranking,
        title match boosting, distance filtering, and constructs detailed source citations.
        """
        candidate_k = max(self.top_k * 3, 12)

        
        # Primary search with exact user query
        raw_results = self.vector_store.similarity_search_with_score(query, k=candidate_k)
        
        # Expanded multi-query search for short topic queries
        expanded_q = build_expanded_query(query)
        if expanded_q != query:
            expanded_results = self.vector_store.similarity_search_with_score(expanded_q, k=candidate_k)
        else:
            expanded_results = []
            
        # Merge candidate results avoiding duplicates
        seen_candidates = set()
        combined_candidates = []
        
        for doc, raw_score in raw_results + expanded_results:
            chunk_id = doc.metadata.get("chunk_id") or doc.page_content[:100]
            if chunk_id not in seen_candidates:
                seen_candidates.add(chunk_id)
                combined_candidates.append((doc, raw_score))

        query_terms = extract_query_terms(query)
        scored_candidates = []
        
        for doc, raw_score in combined_candidates:
            # FAISS returns L2 distance for normalized vectors (0.0 = identical, 2.0 = orthogonal)
            vector_sim = max(0.0, 1.0 - (raw_score / 2.0))
            
            doc_name = doc.metadata.get("document_name", "")
            section_name = doc.metadata.get("section_name", "")
            doc_title = doc.metadata.get("doc_title", "")
            full_chunk_text = f"{doc_title} {doc_name} {section_name} {doc.page_content}"
            
            keyword_ratio = compute_keyword_match_ratio(query, full_chunk_text)
            
            # Title / Heading boost: if query terms match section or document title
            header_text = f"{doc_title} {doc_name} {section_name}".lower()
            header_match_count = sum(1 for term in query_terms if term in header_text) if query_terms else 0
            title_boost = 0.15 if (header_match_count > 0 and len(query_terms) > 0) else 0.0

            # Hybrid Score Fusion: 60% Vector Similarity + 40% Keyword Density + Title Boost
            hybrid_score = (vector_sim * 0.60) + (keyword_ratio * 0.40) + title_boost
            scored_candidates.append((doc, raw_score, vector_sim, hybrid_score))

        # Sort candidates by hybrid score descending
        scored_candidates.sort(key=lambda x: x[3], reverse=True)

        filtered_results: List[Tuple[Document, float]] = []
        sources: List[SourceMetadata] = []
        retrieved_chunks_dto: List[RetrievedChunk] = []
        seen_sources = set()

        for doc, raw_score, vector_sim, hybrid_score in scored_candidates:
            if len(filtered_results) >= self.top_k:
                break
                
            effective_score = max(vector_sim, hybrid_score)
            if effective_score < self.similarity_threshold:
                logger.info(f"Filtering low similarity chunk '{doc.metadata.get('document_name')}' score={effective_score:.4f} < threshold={self.similarity_threshold}")
                continue

            filtered_results.append((doc, raw_score))
            
            chunk_id = doc.metadata.get("chunk_id", f"chunk_{len(retrieved_chunks_dto)}")
            retrieved_chunks_dto.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    content=doc.page_content,
                    metadata=doc.metadata,
                    similarity_score=round(effective_score, 4)
                )
            )
            
            doc_name = doc.metadata.get("document_name", "GitLab Documentation")
            section_name = doc.metadata.get("section_name", "General")
            source_url = doc.metadata.get("source_url", "")
            page_num = doc.metadata.get("page_number", None)
            doc_type = doc.metadata.get("document_type", "markdown")
            
            source_key = (doc_name, section_name, page_num)
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                snippet = doc.page_content[:200].replace("\n", " ").strip() + "..."
                sources.append(
                    SourceMetadata(
                        document_name=doc_name,
                        section_name=section_name,
                        page_number=page_num,
                        source_url=source_url,
                        document_type=doc_type,
                        score=round(effective_score, 4),
                        chunk_snippet=snippet
                    )
                )

        return filtered_results, sources, retrieved_chunks_dto

