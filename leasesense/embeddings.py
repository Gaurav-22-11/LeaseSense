from __future__ import annotations

import hashlib
import math
import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from leasesense.config import settings


class Embedder:
    fallback_dimension = 384

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = None
        self.using_fallback = False
        self.load_error = ""
        try:
            self.model = SentenceTransformer(
                model_name,
                local_files_only=not settings.allow_model_download,
            )
        except Exception as exc:
            self.using_fallback = True
            self.load_error = str(exc)

    @property
    def dimension(self) -> int:
        if self.model is None:
            return self.fallback_dimension
        return self.model.get_sentence_embedding_dimension()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            return [_hash_embed(text, self.fallback_dimension) for text in texts]
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text: str) -> list[float]:
        if self.model is None:
            return _hash_embed(text, self.fallback_dimension)
        vector = self.model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0]
        return vector.tolist()


def _hash_embed(text: str, dimension: int) -> list[float]:
    vector = [0.0] * dimension
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
        bucket = int.from_bytes(digest[:4], "little") % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[bucket] += sign

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


@lru_cache(maxsize=2)
def get_embedder(model_name: str) -> Embedder:
    return Embedder(model_name)
