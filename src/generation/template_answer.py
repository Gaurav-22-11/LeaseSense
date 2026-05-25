from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuestionIntent:
    label: str
    risk_names: tuple[str, ...]
    explanation: str
    next_steps: tuple[str, ...]


INTENTS = {
    "joint_liability": QuestionIntent(
        label="roommate or rent responsibility",
        risk_names=("Joint Liability",),
        explanation=(
            "Your question appears to be about whether tenants or roommates are "
            "responsible together for rent or lease obligations."
        ),
        next_steps=(
            "Ask the landlord to explain whether each tenant is responsible for the full rent or only their share.",
            "If roommates are involved, compare the lease language with any roommate agreement.",
        ),
    ),
    "subleasing": QuestionIntent(
        label="sublease, sublet, assignment, or replacement tenant",
        risk_names=("Subleasing Restrictions",),
        explanation=(
            "Your question appears to be about replacing yourself, subletting, "
            "or assigning the lease to someone else."
        ),
        next_steps=(
            "Look for any requirement that landlord consent must be written and given before a sublease or assignment.",
            "Ask what documents or screening steps are required before another person can take over.",
        ),
    ),
    "early_termination": QuestionIntent(
        label="early move-out or lease termination",
        risk_names=("Early Termination",),
        explanation=(
            "Your question appears to be about ending the lease early or moving "
            "out before the term ends."
        ),
        next_steps=(
            "Ask the landlord for a written payoff or fee estimate before deciding to move out early.",
            "Check local tenant resources because early-termination rules can depend on state or city law.",
        ),
    ),
    "occupancy": QuestionIntent(
        label="guests, occupants, or unauthorized residents",
        risk_names=("Occupancy Limits", "Unauthorized Occupants"),
        explanation=(
            "Your question appears to be about who may stay in the unit, how "
            "long guests may stay, or when a guest becomes an occupant."
        ),
        next_steps=(
            "Ask the landlord to clarify guest limits, approval rules, and when written permission is required.",
            "If someone plans to stay regularly, get approval terms in writing before they move in.",
        ),
    ),
}


def generate_template_answer(
    user_question: str,
    retrieved_chunks: list,
    detected_risks: list,
) -> str:
    """Generate a structured lease answer without using an LLM.

    The function intentionally stays conservative: it summarizes what the
    retrieved lease text appears to address, shows exact snippets, and avoids
    making legal conclusions beyond the evidence.
    """
    intent = _classify_question(user_question)
    matching_risks = _matching_risks(intent, detected_risks)
    evidence_texts = _evidence_texts(retrieved_chunks)
    risk_level = _risk_level(matching_risks, evidence_texts)

    explanation = _build_explanation(user_question, intent, matching_risks, evidence_texts)
    evidence = _format_evidence(evidence_texts)
    next_steps = _format_next_steps(intent, matching_risks, evidence_texts)
    uncertainty = _uncertainty_note(evidence_texts, matching_risks)

    return (
        "## Plain English Explanation\n"
        f"{explanation}\n\n"
        "## Relevant Lease Evidence\n"
        f"{evidence}\n\n"
        "## Risk Level\n"
        f"{risk_level}\n\n"
        "## Suggested Next Steps\n"
        f"{next_steps}\n\n"
        "## Uncertainty / Verify with landlord or legal aid\n"
        f"{uncertainty}"
    )


def _classify_question(question: str) -> QuestionIntent | None:
    normalized = question.lower()
    if any(term in normalized for term in ("roommate", "co-tenant", "cotenant", "rent responsibility", "responsible for rent", "joint", "several")):
        return INTENTS["joint_liability"]
    if any(term in normalized for term in ("sublease", "sublet", "assign", "assignment", "replacement", "take over")):
        return INTENTS["subleasing"]
    if any(term in normalized for term in ("early move", "move out early", "terminate", "termination", "break the lease", "break lease")):
        return INTENTS["early_termination"]
    if any(term in normalized for term in ("guest", "occupant", "occupancy", "unauthorized occupant", "resident", "live with me")):
        return INTENTS["occupancy"]
    return None


def _matching_risks(intent: QuestionIntent | None, detected_risks: list) -> list:
    if intent is None:
        return [risk for risk in detected_risks if getattr(risk, "evidence", None)]
    names = set(intent.risk_names)
    return [risk for risk in detected_risks if getattr(risk, "name", "") in names]


def _evidence_texts(retrieved_chunks: list) -> list[str]:
    texts: list[str] = []
    for chunk in retrieved_chunks:
        text = getattr(chunk, "text", str(chunk)).strip()
        if text:
            texts.append(text)
    return texts


def _risk_level(risks: list, evidence_texts: list[str]) -> str:
    if not evidence_texts:
        return "Unknown"
    if not risks:
        return "Unclear"
    rank = {"low": 1, "medium": 2, "high": 3}
    highest = max(risks, key=lambda risk: rank.get(getattr(getattr(risk, "level", ""), "value", str(getattr(risk, "level", ""))).lower(), 0))
    level = getattr(getattr(highest, "level", ""), "value", str(getattr(highest, "level", "unclear")))
    return level.title() if level else "Unclear"


def _build_explanation(
    question: str,
    intent: QuestionIntent | None,
    matching_risks: list,
    evidence_texts: list[str],
) -> str:
    if not evidence_texts:
        return (
            "I could not find lease language that clearly answers this question. "
            "Because there is no retrieved clause to rely on, LeaseSense cannot "
            "give a confident explanation."
        )

    if intent is None:
        return (
            "The retrieved lease text may be relevant to your question, but it "
            "does not match one of the built-in risk categories closely enough "
            "for a specific rule-based conclusion. Review the evidence below and "
            "verify the meaning before relying on it."
        )

    risk_summaries = [
        getattr(risk, "summary", "")
        for risk in matching_risks
        if getattr(risk, "summary", "")
    ]
    if risk_summaries:
        return f"{intent.explanation} {' '.join(risk_summaries)} The answer should be treated as evidence-based guidance, not a legal conclusion."

    return (
        f"{intent.explanation} The retrieved lease text may be relevant, but "
        "the risk radar did not find a clear matching clause. The lease language "
        "should be verified before you rely on it."
    )


def _format_evidence(evidence_texts: list[str]) -> str:
    if not evidence_texts:
        return "No matching lease snippets were retrieved."
    return "\n\n".join(f"**Evidence {index}**\n\n> {text}" for index, text in enumerate(evidence_texts, start=1))


def _format_next_steps(
    intent: QuestionIntent | None,
    matching_risks: list,
    evidence_texts: list[str],
) -> str:
    steps: list[str] = []
    if intent is not None:
        steps.extend(intent.next_steps)
    else:
        steps.extend(
            (
                "Ask the landlord where this issue is addressed in the lease.",
                "Compare the retrieved language with any addenda, house rules, or renewal documents.",
            )
        )
    if matching_risks and any(getattr(getattr(risk, "level", ""), "value", "") == "high" for risk in matching_risks):
        steps.append("Consider contacting a tenant legal aid group before taking action.")
    if not evidence_texts:
        steps.append("Try rephrasing the question or uploading a clearer copy of the lease.")
    return "\n".join(f"- {step}" for step in steps)


def _uncertainty_note(evidence_texts: list[str], matching_risks: list) -> str:
    if not evidence_texts:
        return (
            "The lease language is unclear because no relevant text was retrieved. "
            "Verify this with your landlord or a local legal aid organization."
        )
    if not matching_risks:
        return (
            "The retrieved text may not contain the full context. Do not treat this "
            "as a legal conclusion; verify the clause with your landlord or legal aid."
        )
    return (
        "This is a rule-based reading of retrieved lease snippets only. LeaseSense "
        "is not legal advice, and unclear or high-stakes issues should be verified "
        "with your landlord or a qualified tenant legal aid organization."
    )
