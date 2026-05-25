from __future__ import annotations

from leasesense.llm.base import GenerationRequest, LLMProvider
from src.generation.template_answer import generate_template_answer


class TemplateProvider(LLMProvider):
    name = "template"

    def generate(self, request: GenerationRequest) -> str:
        return generate_template_answer(
            user_question=request.question,
            retrieved_chunks=request.evidence,
            detected_risks=request.detected_risks,
        )

