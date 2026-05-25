from __future__ import annotations

from functools import lru_cache

from leasesense.config import settings
from leasesense.llm.base import LLMProvider
from leasesense.llm.llama_cpp import LlamaCppProvider
from leasesense.llm.ollama import OllamaProvider
from leasesense.llm.template import TemplateProvider
from leasesense.llm.transformers import TransformersProvider


@lru_cache(maxsize=4)
def build_llm_provider(backend: str | None = None) -> LLMProvider:
    resolved = (backend or settings.llm_backend).strip().lower()
    if resolved in {"template", "rules", "offline"}:
        return TemplateProvider()
    if resolved == "ollama":
        return OllamaProvider()
    if resolved in {"llama_cpp", "llamacpp", "llama.cpp"}:
        return LlamaCppProvider()
    if resolved in {"transformers", "huggingface", "hf"}:
        return TransformersProvider()
    raise ValueError(
        f"Unknown LLM_BACKEND={resolved!r}. Use template, ollama, llama_cpp, or transformers."
    )

