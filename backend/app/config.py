"""Central configuration. Every value can be overridden with an environment
variable (or a .env file in the project root)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:  # optional
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except Exception:  # pragma: no cover
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if v not in (None, "") else default


def _path(name: str, default: Path) -> Path:
    v = _env(name)
    p = Path(v) if v else default
    return p if p.is_absolute() else (PROJECT_ROOT / p)


@dataclass
class Settings:
    # ---- data / storage -------------------------------------------------
    data_dir: Path = field(default_factory=lambda: _path("DATA_DIR", PROJECT_ROOT / "data"))
    storage_dir: Path = field(default_factory=lambda: _path("STORAGE_DIR", PROJECT_ROOT / "storage"))
    log_dir: Path = field(default_factory=lambda: _path("LOG_DIR", PROJECT_ROOT / "logs"))

    # ---- chunking -------------------------------------------------------
    chunk_target_chars: int = int(_env("CHUNK_TARGET_CHARS", "1000"))
    chunk_max_chars: int = int(_env("CHUNK_MAX_CHARS", "1400"))
    chunk_min_chars: int = int(_env("CHUNK_MIN_CHARS", "250"))
    chunk_overlap_chars: int = int(_env("CHUNK_OVERLAP_CHARS", "150"))
    excel_rows_per_chunk: int = int(_env("EXCEL_ROWS_PER_CHUNK", "10"))

    # ---- embeddings -----------------------------------------------------
    embedding_model: str = _env("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    # Optional local folder holding the ONNX model (for offline machines).
    embedding_model_path: str | None = _env("EMBEDDING_MODEL_PATH")
    embedding_batch_size: int = int(_env("EMBEDDING_BATCH_SIZE", "32"))

    # ---- Qdrant ---------------------------------------------------------
    # If QDRANT_URL is set a Qdrant server is used, otherwise embedded
    # (on-disk) Qdrant under storage/qdrant.
    qdrant_url: str | None = _env("QDRANT_URL")
    qdrant_api_key: str | None = _env("QDRANT_API_KEY")
    collection: str = _env("QDRANT_COLLECTION", "india_earthquake_kb")

    # ---- retrieval ------------------------------------------------------
    dense_candidates: int = int(_env("DENSE_CANDIDATES", "30"))
    keyword_candidates: int = int(_env("KEYWORD_CANDIDATES", "30"))
    top_k: int = int(_env("TOP_K", "8"))
    rrf_k: int = int(_env("RRF_K", "60"))
    dense_weight: float = float(_env("DENSE_WEIGHT", "1.0"))
    keyword_weight: float = float(_env("KEYWORD_WEIGHT", "1.0"))
    summary_boost: float = float(_env("SUMMARY_BOOST", "1.15"))
    max_chunks_per_source: int = int(_env("MAX_CHUNKS_PER_SOURCE", "4"))
    # Evidence gate: below this best dense cosine the question is treated as
    # out-of-scope and the LLM is not called.
    min_dense_score: float = float(_env("MIN_DENSE_SCORE", "0.60"))

    # ---- generation -----------------------------------------------------
    # auto | anthropic | openai | extractive
    llm_provider: str = _env("LLM_PROVIDER", "auto")
    llm_model: str | None = _env("LLM_MODEL")
    llm_max_tokens: int = int(_env("LLM_MAX_TOKENS", "1200"))
    anthropic_api_key: str | None = _env("ANTHROPIC_API_KEY")
    openai_api_key: str | None = _env("OPENAI_API_KEY")
    openai_base_url: str | None = _env("OPENAI_BASE_URL")
    # none | llm  -> optional LLM query rewriting before retrieval
    query_rewrite: str = _env("QUERY_REWRITE", "none")

    @property
    def qdrant_path(self) -> Path:
        return self.storage_dir / "qdrant"

    @property
    def manifest_path(self) -> Path:
        return self.storage_dir / "manifest.json"

    def ensure_dirs(self) -> None:
        for d in (self.storage_dir, self.log_dir):
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()
