export interface SourceMetadata {
  document_name: string;
  section_name?: string;
  page_number?: number;
  source_url?: string;
  document_type: string;
  score: number;
  chunk_snippet: string;
}

export interface RetrievedChunk {
  chunk_id: string;
  content: string;
  metadata: Record<string, any>;
  similarity_score: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceMetadata[];
  retrieved_chunks?: RetrievedChunk[];
  timestamp: string;
  error?: string;
}

export interface DocumentItem {
  document_name: string;
  chunk_count: number;
  file_size_bytes: number;
  source_url?: string;
  document_type: string;
}

export interface DocumentListResponse {
  total_documents: number;
  total_chunks: number;
  documents: DocumentItem[];
}

export interface IngestResponse {
  message: string;
  documents_processed: number;
  total_chunks: number;
  total_vectors: number;
}

export interface EvalResultItem {
  question_id: string;
  question: string;
  category: string;
  retrieved_chunks_count: number;
  answer_snippet: string;
  sources: string[];
  is_grounded: boolean;
  relevance_score: number;
  execution_time_sec: number;
}

export interface EvalResponse {
  timestamp: string;
  total_questions: number;
  avg_latency_sec: number;
  grounded_rate_pct: number;
  results: EvalResultItem[];
}

export interface HealthStatus {
  status: string;
  app_name: string;
  version: string;
  embedding_model: string;
  vector_count: number;
  vector_index_ready: boolean;
  ollama_service_ready: boolean;
  ollama_model: string;
  ollama_base_url?: string;
}
