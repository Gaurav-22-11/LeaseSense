from __future__ import annotations

import requests

from leasesense.config import settings
from leasesense.llm.base import GenerationRequest, LLMProvider, SYSTEM_PROMPT, format_rag_prompt


class OllamaProvider(LLMProvider):
    name = "ollama"

    def generate(self, request: GenerationRequest) -> str:
        url = f"{settings.ollama_base_url.rstrip('/')}/api/chat"
        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": format_rag_prompt(request)},
            ],
            "options": {"temperature": 0.2},
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                "Could not reach Ollama. Make sure `ollama serve` is running and "
                f"`ollama pull {settings.ollama_model}` has completed."
            ) from exc

        content = response.json().get("message", {}).get("content", "")
        if not content.strip():
            raise RuntimeError("Ollama returned an empty response.")
        return content

