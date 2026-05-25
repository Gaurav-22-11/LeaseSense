from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from leasesense.config import settings
from leasesense.models import RetrievedEvidence

if TYPE_CHECKING:
    from leasesense.embeddings import Embedder
    from leasesense.vector_store import LeaseVectorStore


@dataclass(frozen=True)
class RetrievalQuery:
    lease_id: str
    question: str
    top_k: int = settings.top_k
    section: str | None = None


class LeaseRetriever:
    def __init__(self, embedder: "Embedder", vector_store: "LeaseVectorStore") -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: RetrievalQuery) -> list[RetrievedEvidence]:
        query_vector = self.embedder.embed_query(query.question)
        return self.vector_store.search(
            lease_id=query.lease_id,
            query_vector=query_vector,
            top_k=query.top_k,
            section=query.section,
        )
