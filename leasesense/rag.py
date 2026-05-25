from __future__ import annotations

from leasesense.config import settings
from leasesense.embeddings import Embedder
from leasesense.llm.base import GenerationRequest
from leasesense.llm.factory import build_llm_provider
from leasesense.models import LeaseAnswer, RiskFinding
from leasesense.retrieval.retriever import LeaseRetriever, RetrievalQuery
from leasesense.vector_store import LeaseVectorStore


def answer_question(
    question: str,
    lease_id: str,
    embedder: Embedder,
    vector_store: LeaseVectorStore,
    detected_risks: list[RiskFinding] | None = None,
    llm_backend: str | None = None,
    section: str | None = None,
) -> LeaseAnswer:
    retriever = LeaseRetriever(embedder=embedder, vector_store=vector_store)
    evidence = retriever.retrieve(
        RetrievalQuery(lease_id=lease_id, question=question, top_k=settings.top_k, section=section)
    )
    if not evidence:
        return LeaseAnswer(
            question=question,
            answer_markdown=(
                "## Plain English Explanation\n"
                "I could not find matching lease evidence for that question.\n\n"
                "## Relevant Lease Evidence\n"
                "No matching chunks were retrieved.\n\n"
                "## Risk Level\n"
                "Unknown\n\n"
                "## Suggested Next Steps\n"
                "Try rephrasing the question or confirm that the lease uploaded correctly.\n\n"
                "## Uncertainty / Verify with landlord or legal aid\n"
                "LeaseSense is not legal advice. Verify unclear issues with your landlord or legal aid."
            ),
            evidence=[],
        )
    provider = build_llm_provider(llm_backend)
    answer = provider.generate(
        GenerationRequest(
            question=question,
            evidence=evidence,
            detected_risks=detected_risks or [],
        )
    )
    return LeaseAnswer(question=question, answer_markdown=answer, evidence=evidence)
