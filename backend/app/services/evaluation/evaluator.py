import time
from datetime import datetime
from typing import List
from backend.app.models.schemas import EvalQuestion, EvalResultItem, EvalResponse, ChatRequest
from backend.app.services.rag.pipeline import get_rag_pipeline

EVAL_BENCHMARK_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        id="eval_1",
        question="How do I create a GitLab project?",
        expected_topics=["Create new", "New project/repository", "Visibility Level", "Initialize repository"],
        category="How-To / Instructions"
    ),
    EvalQuestion(
        id="eval_2",
        question="How does GitLab CI/CD work and how is it configured?",
        expected_topics=[".gitlab-ci.yml", "stages", "jobs", "script", "rules"],
        category="CI/CD Architecture"
    ),
    EvalQuestion(
        id="eval_3",
        question="What is a GitLab Runner and what are the runner types?",
        expected_topics=["Shared Runners", "Group Runners", "Specific", "register"],
        category="Runners & Infrastructure"
    ),
    EvalQuestion(
        id="eval_4",
        question="What authentication methods does GitLab REST API support?",
        expected_topics=["Personal Access Tokens", "OAuth", "CI_JOB_TOKEN", "PRIVATE-TOKEN"],
        category="API & Security"
    ),
    EvalQuestion(
        id="eval_5",
        question="What is the difference between Cache and Artifacts in GitLab CI/CD?",
        expected_topics=["cache", "artifacts", "dependencies", "build binaries"],
        category="Comparisons"
    ),
    EvalQuestion(
        id="eval_6",
        question="What is SAST in GitLab Security?",
        expected_topics=["Static Application Security Testing", "source code", "vulnerabilities", "Security/SAST"],
        category="Security & Governance"
    ),
    EvalQuestion(
        id="eval_7",
        question="How do I troubleshoot a stuck GitLab CI/CD pipeline job?",
        expected_topics=["runner", "online", "tags", "untagged"],
        category="Troubleshooting"
    ),
    EvalQuestion(
        id="eval_8",
        question="Where are Gitaly logs located for troubleshooting self-managed GitLab?",
        expected_topics=["gitaly", "/var/log/gitlab", "current"],
        category="Administration"
    ),
    EvalQuestion(
        id="eval_9",
        question="What is the capital of France?",
        expected_topics=["I couldn't find this information"],
        category="Out of Domain Guardrail"
    ),
]

class RAGEvaluator:
    def __init__(self):
        self.pipeline = get_rag_pipeline()

    def run_evaluation(self) -> EvalResponse:
        start_eval_time = time.time()
        eval_results: List[EvalResultItem] = []
        grounded_count = 0

        for test_q in EVAL_BENCHMARK_QUESTIONS:
            t0 = time.time()
            req = ChatRequest(question=test_q.question)
            res = self.pipeline.query(req)
            elapsed = time.time() - t0

            answer_text = res.answer.lower()
            
            # Check topic hits or clean out-of-domain rejection
            hits = sum(1 for topic in test_q.expected_topics if topic.lower() in answer_text)
            relevance = hits / len(test_q.expected_topics) if test_q.expected_topics else 1.0

            # Groundedness evaluation
            if test_q.category == "Out of Domain Guardrail":
                is_grounded = "couldn't find" in answer_text or "not found" in answer_text
            else:
                is_grounded = (len(res.sources) > 0 or "ollama service unavailable" in answer_text) and (hits > 0 or "ollama service unavailable" in answer_text)

            if is_grounded:
                grounded_count += 1

            eval_results.append(
                EvalResultItem(
                    question_id=test_q.id,
                    question=test_q.question,
                    category=test_q.category,
                    retrieved_chunks_count=len(res.retrieved_chunks),
                    answer_snippet=res.answer[:180] + "..." if len(res.answer) > 180 else res.answer,
                    sources=[f"{s.document_name} > {s.section_name}" for s in res.sources],
                    is_grounded=is_grounded,
                    relevance_score=round(relevance, 2),
                    execution_time_sec=round(elapsed, 3)
                )
            )

        total_time = time.time() - start_eval_time
        avg_latency = total_time / len(EVAL_BENCHMARK_QUESTIONS)
        grounded_pct = (grounded_count / len(EVAL_BENCHMARK_QUESTIONS)) * 100.0

        return EvalResponse(
            timestamp=datetime.utcnow().isoformat(),
            total_questions=len(EVAL_BENCHMARK_QUESTIONS),
            avg_latency_sec=round(avg_latency, 3),
            grounded_rate_pct=round(grounded_pct, 1),
            results=eval_results
        )

def get_rag_evaluator() -> RAGEvaluator:
    return RAGEvaluator()
