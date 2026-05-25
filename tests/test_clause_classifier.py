from leasesense.ingestion.clause_classifier import classify_clause, enrich_chunks
from leasesense.models import TextChunk


def test_classify_sublease_clause():
    category = classify_clause("Tenant shall not sublease without landlord consent.")

    assert category.section == "Subleasing and Assignment"
    assert category.clause_type == "subleasing"
    assert "subleasing_restriction" in category.risk_tags


def test_enrich_chunks_adds_clause_metadata():
    chunks = [
        TextChunk(
            id="chunk-1",
            text="The security deposit may be used for unpaid rent or damage.",
            index=0,
        )
    ]

    enriched = enrich_chunks(chunks)

    assert enriched[0].section == "Security Deposit"
    assert enriched[0].clause_type == "deposit"
