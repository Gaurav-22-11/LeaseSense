from __future__ import annotations

from leasesense.config import settings
from leasesense.llm.base import GenerationRequest, LLMProvider, SYSTEM_PROMPT, format_rag_prompt


class LlamaCppProvider(LLMProvider):
    name = "llama_cpp"

    def __init__(self) -> None:
        if not settings.llama_cpp_model_path:
            raise RuntimeError("LLAMA_CPP_MODEL_PATH must point to a local GGUF model file.")
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            raise RuntimeError("Install llama-cpp-python to use LLM_BACKEND=llama_cpp.") from exc
        self.model = Llama(
            model_path=settings.llama_cpp_model_path,
            n_ctx=settings.llama_cpp_n_ctx,
            verbose=False,
        )

    def generate(self, request: GenerationRequest) -> str:
        prompt = (
            f"<|system|>\n{SYSTEM_PROMPT}\n"
            f"<|user|>\n{format_rag_prompt(request)}\n"
            "<|assistant|>\n"
        )
        response = self.model(
            prompt,
            max_tokens=700,
            temperature=0.2,
            stop=["<|user|>", "<|system|>"],
        )
        text = response["choices"][0]["text"]
        if not text.strip():
            raise RuntimeError("llama.cpp returned an empty response.")
        return text.strip()

