"""Ingest (or incrementally update) the knowledge base.

Usage (from backend/):
    python -m scripts.ingest              # incremental: only new/changed files
    python -m scripts.ingest --rebuild    # drop the collection and re-ingest all
    python -m scripts.ingest --data-dir /path/to/folder
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.pipeline import ingest  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    report = ingest(args.data_dir, rebuild=args.rebuild)
    print(json.dumps({
        "ingested": [{k: r[k] for k in ("file", "document_name", "document_type", "chunks", "timing_s", "warnings")} for r in report["ingested"]],
        "skipped_unchanged": report["skipped"],
        "removed": report["removed"],
        "errors": report["errors"],
        "total_chunks_in_index": report["total_chunks"],
    }, indent=2))


if __name__ == "__main__":
    main()
