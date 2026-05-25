from __future__ import annotations

import re
from dataclasses import dataclass

from leasesense.models import RiskFinding, RiskLevel


@dataclass(frozen=True)
class RiskRule:
    name: str
    patterns: list[str]
    high_terms: list[str]
    medium_terms: list[str]
    no_match_summary: str
    match_summary: str


RULES = [
    RiskRule(
        name="Joint Liability",
        patterns=[r"joint(?:ly)? and several(?:ly)?", r"joint liability", r"severally liable"],
        high_terms=["jointly and severally", "severally liable"],
        medium_terms=["joint liability", "jointly liable"],
        no_match_summary="No obvious joint-liability clause was detected.",
        match_summary="The lease appears to include language making tenants responsible together for obligations.",
    ),
    RiskRule(
        name="Subleasing Restrictions",
        patterns=[r"subleas\w*", r"assign(?:ment)?", r"landlord(?:'s)? consent"],
        high_terms=["no sublease", "shall not sublease", "without landlord's prior written consent"],
        medium_terms=["sublease", "assignment", "consent"],
        no_match_summary="No obvious subleasing restriction was detected.",
        match_summary="The lease appears to restrict subleasing or assignment.",
    ),
    RiskRule(
        name="Occupancy Limits",
        patterns=[r"occupanc\w*", r"occupants?", r"guests?", r"reside"],
        high_terms=["maximum occupancy", "may not reside", "not reside"],
        medium_terms=["occupant", "guest", "reside"],
        no_match_summary="No obvious occupancy limit was detected.",
        match_summary="The lease appears to limit who may live in or regularly use the unit.",
    ),
    RiskRule(
        name="Deposits",
        patterns=[r"security deposit", r"deposit", r"deduct\w*", r"refund", r"withhold"],
        high_terms=["non-refundable", "forfeit", "withhold", "deduct"],
        medium_terms=["security deposit", "deposit", "refund"],
        no_match_summary="No obvious deposit clause was detected.",
        match_summary="The lease appears to include deposit payment, deduction, or refund language.",
    ),
    RiskRule(
        name="Unauthorized Occupants",
        patterns=[r"unauthorized occupant", r"unauthorized resident", r"not listed", r"without(?: prior)? written consent", r"guest.*days?"],
        high_terms=["unauthorized occupant", "unauthorized resident", "without prior written consent"],
        medium_terms=["not listed", "written consent", "guest"],
        no_match_summary="No obvious unauthorized-occupant clause was detected.",
        match_summary="The lease appears to restrict unapproved residents or long-term guests.",
    ),
    RiskRule(
        name="Early Termination",
        patterns=[r"early termination", r"terminate.*lease", r"break.*lease", r"liquidated damages"],
        high_terms=["liquidated damages", "accelerated rent", "rent due for the remainder"],
        medium_terms=["early termination", "termination fee", "break lease"],
        no_match_summary="No obvious early-termination penalty was detected.",
        match_summary="The lease appears to discuss fees, limits, or procedures for ending the lease early.",
    ),
]


def _sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text)
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", compact) if sentence.strip()]


def _find_evidence(text: str, patterns: list[str], limit: int = 3) -> list[str]:
    sentences = _sentences(text)
    matches: list[str] = []
    for sentence in sentences:
        if any(re.search(pattern, sentence, flags=re.IGNORECASE) for pattern in patterns):
            matches.append(sentence[:700])
        if len(matches) >= limit:
            break
    return matches


def _level(evidence: list[str], rule: RiskRule) -> RiskLevel:
    if not evidence:
        return RiskLevel.LOW
    evidence_text = " ".join(evidence).lower()
    if any(term in evidence_text for term in rule.high_terms):
        return RiskLevel.HIGH
    if any(term in evidence_text for term in rule.medium_terms):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def analyze_risks(text: str) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    for rule in RULES:
        evidence = _find_evidence(text, rule.patterns)
        level = _level(evidence, rule)
        findings.append(
            RiskFinding(
                name=rule.name,
                level=level,
                summary=rule.match_summary if evidence else rule.no_match_summary,
                evidence=evidence,
            )
        )
    return findings
