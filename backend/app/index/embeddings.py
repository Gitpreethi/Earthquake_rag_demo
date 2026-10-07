"""Dense embeddings via FastEmbed (ONNX, CPU-friendly, no PyTorch).

Default model: BAAI/bge-small-en-v1.5 (384-d). Queries use the model's
retrieval instruction prefix (FastEmbed's query_embed).
"""
from __future__ import annotations

import logging
from functools import lru_cache

import numpy as np

from ..config import settings

log = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name: str | None = None, model_path: str | None = None):
        from fastembed import TextEmbedding

        self.model_name = model_name or settings.embedding_model
        kwargs = {}
        path = model_path or settings.embedding_model_path
        if path:
            kwargs["specific_model_path"] = path
        log.info("Loading embedding model %s%s", self.model_name, f" from {path}" if path else "")
        self._model = TextEmbedding(self.model_name, **kwargs)
        self.dim = len(next(iter(self._model.embed(["dimension probe"]))))

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        vecs = list(self._model.embed(texts, batch_size=settings.embedding_batch_size))
        return np.asarray(vecs, dtype=np.float32)

    def embed_query(self, text: str) -> np.ndarray:
        return np.asarray(next(iter(self._model.query_embed(text))), dtype=np.float32)


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    return Embedder()
