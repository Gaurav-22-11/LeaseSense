from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    expected_terms: tuple[str, ...]
    expected_risk: str | None


SMOKE_EVALS = [
    EvalCase(
        id="sublease_permission",
        question="Can I sublease my apartment?",
        expected_terms=("sublease", "consent", "landlord"),
        expected_risk="Subleasing Restrictions",
    ),
    EvalCase(
        id="early_termination_fee",
        question="What happens if I move out early?",
        expected_terms=("early termination", "termination", "fee", "rent"),
        expected_risk="Early Termination",
    ),
    EvalCase(
        id="roommate_liability",
        question="Am I responsible if my roommate does not pay?",
        expected_terms=("joint", "several", "liable", "rent"),
        expected_risk="Joint Liability",
    ),
]

