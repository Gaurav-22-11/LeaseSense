from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from leasesense.config import settings
from leasesense.embeddings import Embedder
from leasesense.ingestion.chunker import chunk_text
from leasesense.ingestion.clause_classifier import enrich_chunks
from leasesense.ingestion.parser import parse_pdf
from leasesense.models import ParsedLease, RiskFinding, TextChunk
from leasesense.risk import analyze_risks
from leasesense.vector_store import LeaseVectorStore


@dataclass(frozen=True)
class IngestionResult:
    lease_id: str
    parsed: ParsedLease
    chunks: list[TextChunk]
    risks: list[RiskFinding]


class LeaseIngestionPipeline:
    def __init__(self, embedder: Embedder, vector_store: LeaseVectorStore) -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    def ingest_pdf(self, pdf_path: Path, lease_id: str | None = None) -> IngestionResult:
        parsed = parse_pdf(pdf_path)
        chunks = enrich_chunks(chunk_text(parsed.text))
        if not chunks:
            raise ValueError("No chunks were produced from the lease text.")

        resolved_lease_id = lease_id or pdf_path.stem
        embeddings = self.embedder.embed_documents([chunk.text for chunk in chunks])
        self.vector_store.upsert_chunks(
            lease_id=resolved_lease_id,
            chunks=chunks,
            embeddings=embeddings,
        )
        return IngestionResult(
            lease_id=resolved_lease_id,
            parsed=parsed,
            chunks=chunks,
            risks=analyze_risks(parsed.text),
        )


def build_default_pipeline(embedder: Embedder) -> LeaseIngestionPipeline:
    return LeaseIngestionPipeline(
        embedder=embedder,
        vector_store=LeaseVectorStore(settings.qdrant_path, settings.collection_name),
    )
