from __future__ import annotations

import re
from dataclasses import dataclass

from leasesense.models import TextChunk


@dataclass(frozen=True)
class ClauseCategory:
    section: str
    clause_type: str
    patterns: tuple[str, ...]
    risk_tags: tuple[str, ...] = ()


CATEGORIES = (
    ClauseCategory(
        section="Security Deposit",
        clause_type="deposit",
        patterns=(r"security deposit", r"\bdeposit\b", r"refund", r"deduct", r"withhold"),
        risk_tags=("deposit_deductions",),
    ),
    ClauseCategory(
        section="Rent and Payments",
        clause_type="rent",
        patterns=(r"\brent\b", r"late fee", r"payment", r"due date"),
        risk_tags=("payment_obligation",),
    ),
    ClauseCategory(
        section="Subleasing and Assignment",
        clause_type="subleasing",
        patterns=(r"subleas\w*", r"sublet", r"assign(?:ment)?", r"transfer.*lease"),
        risk_tags=("subleasing_restriction",),
    ),
    ClauseCategory(
        section="Occupancy and Guests",
        clause_type="occupancy",
        patterns=(r"occupanc\w*", r"occupants?", r"guests?", r"unauthorized resident", r"reside"),
        risk_tags=("occupancy_limit",),
    ),
    ClauseCategory(
        section="Joint Liability",
        clause_type="joint_liability",
        patterns=(r"joint(?:ly)? and several(?:ly)?", r"joint liability", r"severally liable"),
        risk_tags=("joint_liability",),
    ),
    ClauseCategory(
        section="Early Termination",
        clause_type="early_termination",
        patterns=(r"early termination", r"terminate.*lease", r"break.*lease", r"liquidated damages"),
        risk_tags=("early_termination",),
    ),
    ClauseCategory(
        section="Maintenance and Repairs",
        clause_type="maintenance",
        patterns=(r"maintenance", r"repair", r"damage", r"habitability", r"utilities"),
        risk_tags=("maintenance_responsibility",),
    ),
    ClauseCategory(
        section="Rules and Violations",
        clause_type="rules",
        patterns=(r"violation", r"default", r"rules", r"notice", r"evict", r"eviction"),
        risk_tags=("lease_violation",),
    ),
)


def classify_clause(text: str) -> ClauseCategory:
    normalized = text.lower()
    for category in CATEGORIES:
        if any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in category.patterns):
            return category
    return ClauseCategory(section="General Lease Terms", clause_type="general", patterns=())


def enrich_chunks(chunks: list[TextChunk]) -> list[TextChunk]:
    enriched: list[TextChunk] = []
    for chunk in chunks:
        category = classify_clause(chunk.text)
        enriched.append(
            TextChunk(
                id=chunk.id,
                text=chunk.text,
                index=chunk.index,
                section=category.section,
                clause_type=category.clause_type,
                risk_tags=category.risk_tags,
            )
        )
    return enriched
