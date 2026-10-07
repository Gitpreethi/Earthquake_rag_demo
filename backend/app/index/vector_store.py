"""Qdrant vector store (embedded on-disk mode by default, or a server via QDRANT_URL)."""
from __future__ import annotations

import atexit
import logging
from functools import lru_cache
from typing import Iterator

import numpy as np
from qdrant_client import QdrantClient, models

from ..config import settings
from ..ingestion.models import Chunk

log = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, client: QdrantClient | None = None, collection: str | None = None):
        settings.ensure_dirs()
        if client is not None:
            self.client = client
        elif settings.qdrant_url:
            self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        else:
            self.client = QdrantClient(path=str(settings.qdrant_path))
        self.collection = collection or settings.collection

    # ---------------------------------------------------------- schema
    def exists(self) -> bool:
        return self.client.collection_exists(self.collection)

    def ensure_collection(self, dim: int) -> None:
        if self.exists():
            return
        self.client.create_collection(
            self.collection,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )
        if settings.qdrant_url:  # payload indexes only matter on a server
            for f in ("source_file", "document_type", "file_type"):
                self.client.create_payload_index(self.collection, f, models.PayloadSchemaType.KEYWORD)
        log.info("Created collection %s (dim=%d)", self.collection, dim)

    def reset(self) -> None:
        if self.exists():
            self.client.delete_collection(self.collection)

    # ---------------------------------------------------------- writes
    def upsert(self, chunks: list[Chunk], vectors: np.ndarray, batch: int = 128) -> None:
        for i in range(0, len(chunks), batch):
            pts = [
                models.PointStruct(
                    id=c.chunk_id,
                    vector=v.tolist(),
                    payload={**c.metadata, "chunk_id": c.chunk_id, "text": c.text, "embed_text": c.embed_text},
                )
                for c, v in zip(chunks[i:i + batch], vectors[i:i + batch])
            ]
            self.client.upsert(self.collection, points=pts, wait=True)

    def delete_source(self, source_file: str) -> None:
        if not self.exists():
            return
        self.client.delete(
            self.collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(must=[models.FieldCondition(key="source_file", match=models.MatchValue(value=source_file))])
            ),
            wait=True,
        )

    # ---------------------------------------------------------- reads
    def search(self, vector: np.ndarray, limit: int) -> list[tuple[str, float, dict]]:
        if not self.exists():
            return []
        res = self.client.query_points(self.collection, query=vector.tolist(), limit=limit, with_payload=True)
        return [(str(p.id), float(p.score), p.payload or {}) for p in res.points]

    def iter_payloads(self, batch: int = 512) -> Iterator[dict]:
        if not self.exists():
            return
        offset = None
        while True:
            pts, offset = self.client.scroll(self.collection, limit=batch, offset=offset, with_payload=True, with_vectors=False)
            for p in pts:
                yield {"id": str(p.id), **(p.payload or {})}
            if offset is None:
                break

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:  # pragma: no cover
            pass

    def count(self) -> int:
        return self.client.count(self.collection, exact=True).count if self.exists() else 0


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    store = VectorStore()
    atexit.register(store.close)
    return store
