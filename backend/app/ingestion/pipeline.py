"""Repeatable, incremental ingestion: DATA -> CHUNKS -> EMBEDDINGS -> QDRANT.

* New files are ingested, changed files (sha256 differs) are re-ingested,
  removed files are deleted from the index, unchanged files are skipped.
* `rebuild=True` drops the collection and ingests everything again.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from ..config import settings
from ..index.embeddings import get_embedder
from ..index.keyword import get_keyword_index
from ..index.vector_store import get_vector_store
from .chunking import chunk_document
from .loaders import discover_files, file_sha256, load_file, load_overrides

log = logging.getLogger(__name__)


def _read_manifest() -> dict:
    p = settings.manifest_path
    return json.loads(p.read_text()) if p.exists() else {"files": {}}


def _write_manifest(m: dict) -> None:
    settings.manifest_path.write_text(json.dumps(m, indent=2))


def refresh_keyword_index() -> int:
    payloads = list(get_vector_store().iter_payloads())
    get_keyword_index().build(payloads)
    return len(payloads)


def ingest(data_dir: Path | None = None, rebuild: bool = False) -> dict:
    data_dir = Path(data_dir or settings.data_dir)
    settings.ensure_dirs()
    store, embedder = get_vector_store(), get_embedder()
    if rebuild:
        store.reset()
        manifest = {"files": {}}
    else:
        manifest = _read_manifest()
        if not store.exists():          # index was wiped -> manifest is stale
            manifest = {"files": {}}
    store.ensure_collection(embedder.dim)

    overrides = load_overrides(data_dir)
    files = discover_files(data_dir)
    seen: set[str] = set()
    report = {"data_dir": str(data_dir), "ingested": [], "skipped": [], "removed": [], "errors": []}
    preview_path = settings.storage_dir / "chunks_preview.jsonl"

    for path in files:
        rel = path.relative_to(data_dir).as_posix()
        seen.add(rel)
        try:
            sha = file_sha256(path)
            prev = manifest["files"].get(rel)
            if prev and prev.get("sha256") == sha and not rebuild:
                report["skipped"].append(rel)
                continue
            t0 = time.perf_counter()
            store.delete_source(rel)
            doc = load_file(path, data_dir, overrides)
            chunks = chunk_document(doc)
            t1 = time.perf_counter()
            vectors = embedder.embed_documents([c.embed_text for c in chunks]) if chunks else []
            t2 = time.perf_counter()
            if chunks:
                store.upsert(chunks, vectors)
            t3 = time.perf_counter()
            entry = {
                "sha256": sha,
                "document_name": doc.document_name,
                "document_type": doc.document_type,
                "file_type": doc.file_type,
                "chunks": len(chunks),
                "pages": doc.extra.get("page_count"),
                "sheets": list(doc.sheets.keys()) or None,
                "warnings": doc.warnings,
                "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "timing_s": {"load_chunk": round(t1 - t0, 2), "embed": round(t2 - t1, 2), "upsert": round(t3 - t2, 2)},
            }
            manifest["files"][rel] = entry
            _write_manifest(manifest)   # checkpoint after every file
            report["ingested"].append({"file": rel, **entry})
            with preview_path.open("a", encoding="utf-8") as f:
                for c in chunks[:5]:
                    f.write(json.dumps({"source_file": rel, "locator": c.metadata["locator"], "section": c.metadata["section"], "text": c.text[:500]}) + "\n")
            log.info("Ingested %s: %d chunks (%s)", rel, len(chunks), entry["timing_s"])
        except Exception as e:  # keep going with other files
            log.exception("Failed to ingest %s", rel)
            report["errors"].append({"file": rel, "error": repr(e)})

    for rel in list(manifest["files"]):
        if rel not in seen:
            store.delete_source(rel)
            manifest["files"].pop(rel)
            report["removed"].append(rel)
    _write_manifest(manifest)
    report["total_chunks"] = refresh_keyword_index()
    return report


def corpus_summary() -> dict:
    m = _read_manifest()
    return {
        "documents": [{"source_file": k, **{x: v.get(x) for x in ("document_name", "document_type", "file_type", "chunks", "pages", "sheets", "warnings")}} for k, v in m["files"].items()],
        "total_chunks": get_vector_store().count(),
    }
