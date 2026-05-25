from __future__ import annotations

from leasesense.config import settings
from leasesense.llm.base import GenerationRequest, LLMProvider, SYSTEM_PROMPT, format_rag_prompt


class TransformersProvider(LLMProvider):
    name = "transformers"

    def __init__(self) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("Install transformers and torch to use LLM_BACKEND=transformers.") from exc

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.transformers_model,
            local_files_only=not settings.allow_model_download,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            settings.transformers_model,
            local_files_only=not settings.allow_model_download,
            device_map="auto" if torch.cuda.is_available() else None,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )

    def generate(self, request: GenerationRequest) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": format_rag_prompt(request)},
        ]
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prompt = f"{SYSTEM_PROMPT}\n\n{format_rag_prompt(request)}\n\nAnswer:"

        inputs = self.tokenizer(prompt, return_tensors="pt")
        if next(self.model.parameters()).is_cuda:
            inputs = {key: value.to(self.model.device) for key, value in inputs.items()}
        output = self.model.generate(
            **inputs,
            max_new_tokens=settings.transformers_max_new_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        generated = output[0][inputs["input_ids"].shape[-1] :]
        text = self.tokenizer.decode(generated, skip_special_tokens=True)
        if not text.strip():
            raise RuntimeError("Transformers provider returned an empty response.")
        return text.strip()

