# GitLab Product Documentation Helper (Full-Stack RAG Application)

An AI-powered documentation assistant that enables users to ask technical questions about GitLab and receive accurate, grounded answers backed by official GitLab product documentation and source citations.

---

## 1. Project Overview
The **GitLab Product Documentation Helper** is an end-to-end Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, Hugging Face Embeddings, FAISS Vector Database, local Ollama LLM (`llama3.2:1b`), and Next.js React with Tailwind CSS. It runs **100% locally with zero API key requirement**.

## 2. Problem Statement
General LLMs can hallucinate outdated CLI parameters, invalid API endpoints, or inaccurate settings when answering product-specific documentation questions. By anchoring AI generations strictly to retrieved official documentation chunks, this system eliminates hallucination and guarantees verifiable technical answers.

## 3. Objectives
- **Zero Hallucination & Zero API Keys**: 100% local AI pipeline running without third-party API dependencies. Rejects out-of-domain queries when documentation is absent.
- **Verifiable Citations**: Every answer displays exact source files, section headers, matching scores, and official doc URLs.
- **Production Performance**: Local FAISS vector index persistence ensures sub-second retrieval times without rebuilding vector indexes per request.
- **Full Stack Integration**: RESTful FastAPI backend connected to a developer-oriented Next.js frontend workspace.

---

## 4. RAG Workflow Pipeline
```
GitLab Docs → Ingestion → Text Extraction → Cleaning → Chunking → Hugging Face Embeddings → FAISS Store → User Query → Query Embedding → Vector Similarity Search → Top-K Chunks → Grounded Prompt → Ollama LLM (llama3.2:1b) → Answer + Citations
```

---

## 5. Technology Stack
- **Frontend**: Next.js 14+ (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons, React Markdown.
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2.
- **RAG & Vector Database**: LangChain, Hugging Face Embeddings (`all-MiniLM-L6-v2`), FAISS (Facebook AI Similarity Search).
- **LLM**: Ollama (`llama3.2:1b` local model).

---

## 6. Repository Folder Structure
```
GITLAB Documentation helper/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint & CORS
│   │   ├── api/
│   │   │   ├── chat.py                # POST /api/chat
│   │   │   ├── documents.py           # POST /api/ingest, POST /api/reindex, GET /api/documents
│   │   │   ├── evaluation.py          # POST /api/evaluate
│   │   │   └── health.py              # GET /api/health
│   │   ├── config/settings.py         # App configuration & environment variables
│   │   ├── models/schemas.py          # Pydantic data schemas
│   │   ├── services/
│   │   │   ├── ingestion/             # Document loaders & chunkers
│   │   │   ├── embeddings/            # HuggingFace embedding service
│   │   │   ├── vectorstore/           # FAISS index persistence & search
│   │   │   ├── llm/                   # Local Ollama LLM service wrapper
│   │   │   ├── rag/                   # RAG retriever, prompts, & pipeline
│   │   │   └── evaluation/            # RAG benchmark evaluation suite
│   ├── data/sample_docs/              # Indexed GitLab Markdown documentation
│   ├── vectorstore_db/                # Local FAISS index files
│   ├── tests/                         # Pytest test suite
│   ├── requirements.txt
│   └── run.py                         # FastAPI server launcher
├── frontend/                          # Next.js TypeScript application
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── types/
│   └── package.json
├── docs/                              # Technical documentation & architecture diagrams
├── .env.example                       # Environment variables template
├── .env                               # Active configuration file
└── README.md
```

---

## 7. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js v18 or higher (npm 9+)
- Ollama (installed locally, e.g. `ollama pull llama3.2:1b`)

### Step 1: Install & Start Ollama
```bash
# Pull lightweight local model
ollama pull llama3.2:1b
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```
Default `.env` configuration (no API keys needed!):
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.2:1b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TOP_K=4
SIMILARITY_THRESHOLD=0.20
```


### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

---

## 8. Render Cloud Deployment (Production)

This repository includes a native [`render.yaml`](render.yaml) Blueprint manifest for deployment on [Render](https://render.com).

### Render Setup Notes
1. Push this repository to GitHub.
2. Create a new **Blueprint** in the Render dashboard and connect this repository.
3. Render will provision:
   - **`gitlab-rag-backend`** as the Python FastAPI service with the bundled FAISS index and local Ollama startup script.
   - **`gitlab-rag-frontend`** as the Next.js service that calls the backend through `NEXT_PUBLIC_API_URL`.
4. The backend uses the Render-provided `PORT` and binds to `0.0.0.0`, while the frontend starts with `npx next start -H 0.0.0.0 -p $PORT`.
5. No `.env`, API keys, or secrets are included in the repository.

---

## 9. Running Locally


### Start Backend API Server (Port 8000)
```bash
# From workspace root
python backend/run.py
```
*API Swagger Documentation available at `http://localhost:8000/docs`.*

### Start Frontend Application (Port 3000)
```bash
# In a new terminal
cd frontend
npm run dev
```
*Open `http://localhost:3000` in your web browser.*

---

## 9. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/chat` | Send query & dialogue history; get grounded answer & sources |
| `GET` | `/api/documents` | List indexed documents & vector count statistics |
| `POST` | `/api/ingest` | Upload new `.md`, `.pdf`, `.txt`, `.html` document |
| `POST` | `/api/reindex` | Re-scan documentation folder & rebuild FAISS index |
| `POST` | `/api/evaluate` | Trigger automated RAG benchmark evaluation suite |
| `GET` | `/api/health` | Check vector store status & local Ollama service status |

---

## 10. Example Benchmark Questions
1. "How do I create a GitLab project?"
2. "How does GitLab CI/CD work and how is `.gitlab-ci.yml` configured?"
3. "What is a GitLab Runner and how do I register one?"
4. "How do I create a merge request?"
5. "What authentication methods does GitLab API support?"
6. "What is the difference between Issues and Merge Requests?"
7. *"What is the capital of France?"* → *(Safely rejected: "I couldn't find this information in the available GitLab documentation.")*

---

## 11. Testing & RAG Evaluation

### Run Backend Unit & Integration Tests
```bash
python -m pytest backend/tests/ -v
```

### Run Interactive RAG Evaluation
Click the **RAG Evaluation** button in the top navigation bar of the web app or execute `POST /api/evaluate`. This measures:
- Groundedness Rate (%)
- Context Retrieval Relevance
- Execution Latency (seconds)

---

## 12. Future Enhancements
- Support for hybrid BM25 lexical + dense vector retrieval (Reciprocal Rank Fusion).
- Integration with remote vector databases like Qdrant or Pinecone.
- Real-time crawler for syncing official GitLab documentation releases.
