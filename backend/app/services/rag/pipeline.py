import logging
from typing import List, Optional
from backend.app.models.schemas import ChatRequest, ChatResponse, ChatMessage
from backend.app.services.rag.retriever import DocumentRetriever
from backend.app.services.rag.prompt_templates import RAG_PROMPT, format_context_chunks
from backend.app.services.llm.ollama_service import get_ollama_service

from backend.app.services.rag.intent_classifier import detect_query_intent

logger = logging.getLogger(__name__)

def format_conversation_history(history: List[ChatMessage]) -> str:
    """Formats recent conversation history for prompt contextualization."""
    if not history:
        return "No previous conversation."
    
    # Take last 4 turns to avoid prompt token explosion
    recent_history = history[-4:]
    formatted = []
    for msg in recent_history:
        role = "User" if msg.role == "user" else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    return "\n".join(formatted)

class RAGPipeline:
    def __init__(self):
        self.retriever = DocumentRetriever()
        self.llm_service = get_ollama_service()

    def query(self, request: ChatRequest) -> ChatResponse:
        """
        Executes full RAG flow:
        User Question -> FAISS Retrieval -> Context Construction -> Intent Detection -> Ollama Prompting -> Grounded Answer & Citations.
        """
        user_question = request.question.strip()
        if not user_question:
            return ChatResponse(
                answer="Please provide a valid non-empty question.",
                sources=[],
                retrieved_chunks=[]
            )

        # Step 1 & 2: FAISS retrieval & score filtering
        raw_chunks, sources, retrieved_chunks_dto = self.retriever.retrieve(user_question)

        # Out-of-domain check / empty index handling
        if not raw_chunks:
            return ChatResponse(
                answer="I couldn't find this information in the available GitLab documentation.",
                sources=[],
                retrieved_chunks=[]
            )

        # Step 3: Dynamic Intent Detection & Context formatting
        intent = detect_query_intent(user_question)
        
        # For DEFINITION queries, restrict context to top 2 chunks to avoid noisy secondary sections
        selected_chunks = raw_chunks[:2] if intent == "DEFINITION" else raw_chunks
        context_str = format_context_chunks(selected_chunks)
        history_str = format_conversation_history(request.conversation_history or [])


        # Step 4: Prompt Construction
        formatted_prompt = RAG_PROMPT.format(
            context=context_str,
            conversation_history=history_str,
            question=user_question,
            query_intent=intent
        )



        # Step 5: Ollama LLM Generation
        raw_llm_answer = self.llm_service.generate(formatted_prompt)

        # If LLM indicates service unavailable, pass through response
        if "Ollama Service Unavailable" in raw_llm_answer:
            return ChatResponse(
                answer=raw_llm_answer,
                sources=sources,
                retrieved_chunks=retrieved_chunks_dto
            )

        # Groundedness verification check
        fallback_phrase = "I couldn't find this information in the available GitLab documentation."
        if fallback_phrase.lower() in raw_llm_answer.lower():
            return ChatResponse(
                answer=fallback_phrase,
                sources=[],
                retrieved_chunks=retrieved_chunks_dto
            )

        return ChatResponse(
            answer=raw_llm_answer.strip(),
            sources=sources,
            retrieved_chunks=retrieved_chunks_dto
        )

_rag_pipeline_instance: Optional[RAGPipeline] = None

def get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline_instance
    if _rag_pipeline_instance is None:
        _rag_pipeline_instance = RAGPipeline()
    return _rag_pipeline_instance
