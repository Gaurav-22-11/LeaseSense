from leasesense.models import RetrievedEvidence
from leasesense.retrieval.retriever import LeaseRetriever, RetrievalQuery


class FakeEmbedder:
    def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self) -> None:
        self.last_section = None

    def search(self, lease_id: str, query_vector: list[float], top_k: int, section: str | None = None):
        self.last_section = section
        return [
            RetrievedEvidence(
                text="Tenant may not sublease without landlord consent.",
                score=0.9,
                chunk_id="chunk-1",
                section=section or "Subleasing and Assignment",
                clause_type="subleasing",
            )
        ]


def test_retriever_passes_section_filter():
    vector_store = FakeVectorStore()
    retriever = LeaseRetriever(embedder=FakeEmbedder(), vector_store=vector_store)

    evidence = retriever.retrieve(
        RetrievalQuery(
            lease_id="lease-1",
            question="Can I sublease?",
            section="Subleasing and Assignment",
        )
    )

    assert vector_store.last_section == "Subleasing and Assignment"
    assert evidence[0].section == "Subleasing and Assignment"
