from __future__ import annotations

import argparse
import json
from pathlib import Path

from leasesense.config import settings
from leasesense.embeddings import get_embedder
from leasesense.evals.datasets import SMOKE_EVALS
from leasesense.evals.metrics import answer_contains_evidence, retrieval_term_recall, risk_hit
from leasesense.ingestion.pipeline import LeaseIngestionPipeline
from leasesense.rag import answer_question
from leasesense.vector_store import LeaseVectorStore


def run_eval(pdf_path: Path, backend: str = "template") -> dict:
    embedder = get_embedder(settings.embedding_model)
    vector_store = LeaseVectorStore(settings.qdrant_path, settings.collection_name)
    ingestion = LeaseIngestionPipeline(embedder=embedder, vector_store=vector_store)
    ingested = ingestion.ingest_pdf(pdf_path=pdf_path, lease_id=f"eval-{pdf_path.stem}")

    rows = []
    for case in SMOKE_EVALS:
        answer = answer_question(
            question=case.question,
            lease_id=ingested.lease_id,
            embedder=embedder,
            vector_store=vector_store,
            detected_risks=ingested.risks,
            llm_backend=backend,
        )
        rows.append(
            {
                "id": case.id,
                "question": case.question,
                "retrieval_term_recall": retrieval_term_recall(case, answer.evidence),
                "risk_hit": risk_hit(case, ingested.risks),
                "answer_has_evidence_section": answer_contains_evidence(answer.answer_markdown),
            }
        )

    return {
        "lease_id": ingested.lease_id,
        "backend": backend,
        "cases": rows,
        "mean_retrieval_term_recall": sum(row["retrieval_term_recall"] for row in rows) / len(rows),
        "risk_hit_rate": sum(1 for row in rows if row["risk_hit"]) / len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LeaseSense smoke evals against a lease PDF.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--backend", default="template")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = run_eval(args.pdf, backend=args.backend)
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"LeaseSense eval report for {args.pdf}")
    print(f"Backend: {report['backend']}")
    print(f"Mean retrieval term recall: {report['mean_retrieval_term_recall']:.2f}")
    print(f"Risk hit rate: {report['risk_hit_rate']:.2f}")
    for row in report["cases"]:
        print(
            f"- {row['id']}: recall={row['retrieval_term_recall']:.2f}, "
            f"risk_hit={row['risk_hit']}, evidence_section={row['answer_has_evidence_section']}"
        )


if __name__ == "__main__":
    main()

