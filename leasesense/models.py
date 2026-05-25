from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class ParsedLease:
    text: str
    source_name: str


@dataclass(frozen=True)
class TextChunk:
    id: str
    text: str
    index: int
    section: str = "General"
    clause_type: str = "general"
    risk_tags: tuple[str, ...] = ()


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RiskFinding:
    name: str
    level: RiskLevel
    summary: str
    evidence: list[str]


@dataclass(frozen=True)
class RetrievedEvidence:
    text: str
    score: float
    chunk_id: str
    section: str = "General"
    clause_type: str = "general"
    risk_tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class LeaseAnswer:
    question: str
    answer_markdown: str
    evidence: list[RetrievedEvidence]
