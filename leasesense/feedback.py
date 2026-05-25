from __future__ import annotations

import csv
from datetime import datetime, timezone

from leasesense.config import settings


def save_feedback(lease_id: str, question: str, feedback: str, answer: str) -> None:
    settings.feedback_path.parent.mkdir(parents=True, exist_ok=True)
    exists = settings.feedback_path.exists()
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lease_id": lease_id,
        "question": question,
        "feedback": feedback,
        "answer": answer,
    }
    with settings.feedback_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(event.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(event)
