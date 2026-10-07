"""Hybrid retrieval: dense (Qdrant) + keyword (BM25) fused with Reciprocal Rank Fusion."""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field

from ..config import settings
from ..index.embeddings import get_embedder
from ..index.keyword import get_keyword_index
from ..index.vector_store import get_vector_store
from .query import RetrievalQuery, build_query

PUBLIC_META = (
    "document_name", "source_file", "file_type", "document_type", "page_start", "page_end", "pages",
    "sheet", "row_start", "row_end", "locator", "section", "locations", "topics", "chunk_kind", "chunk_index",
)


@dataclass
class Evidence:
    evidence_id: str            # "E1", "E2", ... (used for citations)
    chunk_id: str
    rank: int
    text: str
    metadata: dict
    fused_score: float          # raw RRF score
    relevance: float            # RRF normalised to 0..1
    dense_score: float | None   # cosine similarity
    dense_rank: int | None
    keyword_score: float | None # raw BM25
    keyword_score_norm: float | None
    keyword_rank: int | None
    matched_by: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RetrievalResult:
    query: RetrievalQuery
    evidence: list[Evidence]
    best_dense_score: float
    missing_terms: list[str]
    missing_entities: list[str]
    sufficient: bool
    timings_ms: dict
    candidates: dict


def rrf_fuse(
    dense: list[tuple[str, float, dict]],
    keyword: list[tuple[str, float, dict]],
    k: int = 60,
    w_dense: float = 1.0,
    w_kw: float = 1.0,
) -> list[dict]:
    """Reciprocal Rank Fusion of two ranked lists. Returns merged records sorted by fused score."""
    merged: dict[str, dict] = {}
    max_kw = max((s for _, s, _ in keyword), default=0.0) or 1.0
    for rank, (cid, score, payload) in enumerate(dense, 1):
        r = merged.setdefault(cid, {"id": cid, "payload": payload, "fused": 0.0})
        r.update(dense_score=score, dense_rank=rank)
        r["fused"] += w_dense / (k + rank)
    for rank, (cid, score, payload) in enumerate(keyword, 1):
        r = merged.setdefault(cid, {"id": cid, "payload": payload, "fused": 0.0})
        r.update(keyword_score=score, keyword_score_norm=score / max_kw, keyword_rank=rank)
        r["fused"] += w_kw / (k + rank)
    return sorted(merged.values(), key=lambda r: -r["fused"])


def diversify(records: list[dict], top_k: int, max_per_source: int, max_per_section: int = 2) -> list[dict]:
    """Keep ranking order but cap how many chunks one source file (and one
    section of it, e.g. one region of the seismic catalogue) may contribute,
    so near-duplicate chunks do not crowd out other documents."""
    out, per_src, per_sec, overflow = [], {}, {}, []
    for r in records:
        src = r["payload"].get("source_file", "?")
        sec = (src, r["payload"].get("section"))
        if per_src.get(src, 0) < max_per_source and per_sec.get(sec, 0) < max_per_section:
            out.append(r)
            per_src[src] = per_src.get(src, 0) + 1
            per_sec[sec] = per_sec.get(sec, 0) + 1
        else:
            overflow.append(r)
        if len(out) == top_k:
            return out
    return (out + overflow)[:top_k]   # only one source relevant -> allow more from it


def retrieve(question: str, top_k: int | None = None, rewrite: str | None = None) -> RetrievalResult:
    top_k = top_k or settings.top_k
    t0 = time.perf_counter()
    q = build_query(question, rewrite)
    store, kw_index = get_vector_store(), get_keyword_index()
    if len(kw_index) == 0:          # first request after start-up
        from ..ingestion.pipeline import refresh_keyword_index
        refresh_keyword_index()

    t1 = time.perf_counter()
    qvec = get_embedder().embed_query(q.dense_text)
    dense = store.search(qvec, settings.dense_candidates)
    t2 = time.perf_counter()
    keyword = kw_index.search(q.keyword_tokens, settings.keyword_candidates)
    t3 = time.perf_counter()

    fused = rrf_fuse(dense, keyword, settings.rrf_k, settings.dense_weight, settings.keyword_weight)
    # Mild prior for computed summary chunks (e.g. per-region catalogue summaries):
    # they condense many near-identical event listings into one overview.
    for r in fused:
        if r["payload"].get("chunk_kind") == "summary":
            r["fused"] *= settings.summary_boost
    fused.sort(key=lambda r: -r["fused"])
    picked = diversify(fused, top_k, settings.max_chunks_per_source)
    max_fused = (settings.dense_weight + settings.keyword_weight) / (settings.rrf_k + 1)

    evidence = []
    for i, r in enumerate(picked, 1):
        p = r["payload"]
        matched = [m for m, key in (("vector", "dense_rank"), ("keyword", "keyword_rank")) if r.get(key)]
        evidence.append(Evidence(
            evidence_id=f"E{i}",
            chunk_id=r["id"],
            rank=i,
            text=p.get("text", ""),
            metadata={k: p.get(k) for k in PUBLIC_META},
            fused_score=round(r["fused"], 6),
            relevance=round(min(r["fused"] / max_fused, 1.0), 4),
            dense_score=round(r["dense_score"], 4) if "dense_score" in r else None,
            dense_rank=r.get("dense_rank"),
            keyword_score=round(r["keyword_score"], 3) if "keyword_score" in r else None,
            keyword_score_norm=round(r["keyword_score_norm"], 4) if "keyword_score_norm" in r else None,
            keyword_rank=r.get("keyword_rank"),
            matched_by=matched,
        ))

    best_dense = max((s for _, s, _ in dense), default=0.0)
    missing = kw_index.missing_terms(q.salient_tokens)
    missing_entities = [t for t in q.entity_terms if t in missing]
    sufficient = bool(evidence) and best_dense >= settings.min_dense_score
    t4 = time.perf_counter()
    return RetrievalResult(
        query=q,
        evidence=evidence,
        best_dense_score=round(best_dense, 4),
        missing_terms=missing,
        missing_entities=missing_entities,
        sufficient=sufficient,
        timings_ms={
            "query_processing": round((t1 - t0) * 1000, 1),
            "dense_search": round((t2 - t1) * 1000, 1),
            "keyword_search": round((t3 - t2) * 1000, 1),
            "fusion": round((t4 - t3) * 1000, 1),
            "retrieval_total": round((t4 - t0) * 1000, 1),
        },
        candidates={"dense": len(dense), "keyword": len(keyword), "fused": len(fused)},
    )
