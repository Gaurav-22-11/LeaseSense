from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from leasesense.config import settings
from leasesense.embeddings import get_embedder
from leasesense.rag import answer_question
from leasesense.risk import analyze_risks
from leasesense.vector_store import LeaseVectorStore


app = FastAPI(
    title="LeaseSense API",
    version="0.1.0",
    description="Local-first lease RAG API. Upload ingestion remains in the Streamlit MVP; this API exposes health and question answering.",
)


class AskRequest(BaseModel):
    lease_id: str
    question: str
    lease_text: str | None = None
    llm_backend: str | None = None
    section: str | None = None


class EvidenceResponse(BaseModel):
    chunk_id: str
    score: float
    text: str
    section: str
    clause_type: str
    risk_tags: list[str]


class AskResponse(BaseModel):
    question: str
    answer_markdown: str
    evidence: list[EvidenceResponse]


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "llm_backend": settings.llm_backend,
        "embedding_model": settings.embedding_model,
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    embedder = get_embedder(settings.embedding_model)
    vector_store = LeaseVectorStore(settings.qdrant_path, settings.collection_name)
    risks = analyze_risks(request.lease_text) if request.lease_text else []
    answer = answer_question(
        question=request.question,
        lease_id=request.lease_id,
        embedder=embedder,
        vector_store=vector_store,
        detected_risks=risks,
        llm_backend=request.llm_backend,
        section=request.section,
    )
    return AskResponse(
        question=answer.question,
        answer_markdown=answer.answer_markdown,
        evidence=[
            EvidenceResponse(
                chunk_id=item.chunk_id,
                score=item.score,
                text=item.text,
                section=item.section,
                clause_type=item.clause_type,
                risk_tags=list(item.risk_tags),
            )
            for item in answer.evidence
        ],
    )
