from leasesense.llm.base import GenerationRequest
from leasesense.llm.template import TemplateProvider
from leasesense.models import RetrievedEvidence


def test_template_provider_returns_required_sections():
    provider = TemplateProvider()
    answer = provider.generate(
        GenerationRequest(
            question="Can I sublease?",
            evidence=[
                RetrievedEvidence(
                    text="Tenant may not sublease without landlord consent.",
                    score=0.9,
                    chunk_id="chunk-1",
                )
            ],
            detected_risks=[],
        )
    )

    assert "## Plain English Explanation" in answer
    assert "## Relevant Lease Evidence" in answer
    assert "## Risk Level" in answer
    assert "## Suggested Next Steps" in answer

