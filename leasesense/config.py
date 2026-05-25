from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_root: Path = Path(__file__).resolve().parents[1]
    data_dir: Path = Path(os.getenv("LEASESENSE_DATA_DIR", "data"))
    qdrant_path: Path = Path(os.getenv("QDRANT_PATH", "data/qdrant"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    feedback_path: Path = Path(os.getenv("FEEDBACK_PATH", "data/feedback.csv"))
    collection_name: str = os.getenv("QDRANT_COLLECTION", "lease_chunks")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    allow_model_download: bool = os.getenv("ALLOW_MODEL_DOWNLOAD", "false").lower() in {"1", "true", "yes"}
    enable_ocr: bool = os.getenv("ENABLE_OCR", "false").lower() in {"1", "true", "yes"}
    llm_backend: str = os.getenv("LLM_BACKEND", "template")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    llama_cpp_model_path: str = os.getenv("LLAMA_CPP_MODEL_PATH", "")
    llama_cpp_n_ctx: int = int(os.getenv("LLAMA_CPP_N_CTX", "4096"))
    transformers_model: str = os.getenv("TRANSFORMERS_MODEL", "Qwen/Qwen2.5-3B-Instruct")
    transformers_max_new_tokens: int = int(os.getenv("TRANSFORMERS_MAX_NEW_TOKENS", "700"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "160"))
    top_k: int = int(os.getenv("TOP_K", "5"))
    preview_char_limit: int = int(os.getenv("PREVIEW_CHAR_LIMIT", "20000"))


settings = Settings()
