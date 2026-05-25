from __future__ import annotations

from leasesense.evals.datasets import EvalCase
from leasesense.models import RetrievedEvidence, RiskFinding


def retrieval_term_recall(case: EvalCase, evidence: list[RetrievedEvidence]) -> float:
    haystack = " ".join(item.text.lower() for item in evidence)
    if not case.expected_terms:
        return 1.0
    hits = sum(1 for term in case.expected_terms if term.lower() in haystack)
    return hits / len(case.expected_terms)


def risk_hit(case: EvalCase, risks: list[RiskFinding]) -> bool:
    if case.expected_risk is None:
        return True
    return any(risk.name == case.expected_risk and risk.evidence for risk in risks)


def answer_contains_evidence(answer_markdown: str) -> bool:
    lowered = answer_markdown.lower()
    return "relevant lease evidence" in lowered and "evidence" in lowered

