from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from leasesense.models import RetrievedEvidence, RiskFinding


@dataclass(frozen=True)
class GenerationRequest:
    question: str
    evidence: list[RetrievedEvidence]
    detected_risks: list[RiskFinding]


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, request: GenerationRequest) -> str:
        raise NotImplementedError


SYSTEM_PROMPT = """You are LeaseSense, a careful lease analysis assistant for renters.
Use only the provided lease evidence. If evidence is insufficient, say what is missing.
Do not provide legal advice. Use plain English and recommend landlord clarification or tenant legal aid for high-stakes decisions.
Return exactly these sections:
## Plain English Explanation
## Relevant Lease Evidence
## Risk Level
## Suggested Next Steps
## Uncertainty / Verify with landlord or legal aid
"""


def format_rag_prompt(request: GenerationRequest) -> str:
    evidence_text = "\n\n".join(
        f"[Evidence {idx} | section {item.section} | score {item.score:.3f} | chunk {item.chunk_id}]\n{item.text}"
        for idx, item in enumerate(request.evidence, start=1)
    )
    risks = "\n".join(
        f"- {risk.name}: {risk.level.value.upper()} - {risk.summary}"
        for risk in request.detected_risks
    ) or "- No rule-based risks were detected."
    return f"""Question:
{request.question}

Retrieved lease evidence:
{evidence_text}

Rule-based risk radar:
{risks}

Answer using only the retrieved lease evidence and the risk radar context."""
