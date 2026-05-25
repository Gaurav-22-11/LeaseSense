from __future__ import annotations

import re
import uuid

from leasesense.config import settings
from leasesense.models import TextChunk


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[TextChunk]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    clean = normalize_text(text)
    if not clean:
        return []

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", clean) if part.strip()]
    chunks: list[TextChunk] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if not current:
            return
        chunk_body = "\n\n".join(current).strip()
        chunks.append(TextChunk(id=str(uuid.uuid4()), text=chunk_body, index=len(chunks)))
        if overlap > 0:
            tail = chunk_body[-overlap:]
            current = [tail]
            current_len = len(tail)
        else:
            current = []
            current_len = 0

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            flush()
            for start in range(0, len(paragraph), max(1, chunk_size - overlap)):
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(TextChunk(id=str(uuid.uuid4()), text=piece, index=len(chunks)))
            current = []
            current_len = 0
            continue

        next_len = current_len + len(paragraph) + 2
        if next_len > chunk_size:
            flush()
        current.append(paragraph)
        current_len += len(paragraph) + 2

    flush()
    return chunks
