"""Run the RAG test set end to end and write a verifiable report.

Usage (from backend/):
    python -m scripts.run_tests                 # uses tests/test_queries.json
    python -m scripts.run_tests --top-k 8

Writes reports/test_report.md and reports/test_report.json with, per query,
the answer, its status, and every retrieved source (document, page/sheet,
scores), plus retrieval metrics: Hit@k, MRR and source recall.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import PROJECT_ROOT  # noqa: E402
from app.generation.llm import get_llm  # noqa: E402
from app.generation.rag import answer_question  # noqa: E402


def score_retrieval(evidence: list[dict], expected: list[str]) -> dict:
    files = [e["metadata"]["source_file"] for e in evidence]
    first = next((i + 1 for i, f in enumerate(files) if any(x in f for x in expected)), None)
    found = [x for x in expected if any(x in f for f in files)]
    return {
        "hit": first is not None,
        "reciprocal_rank": round(1 / first, 3) if first else 0.0,
        "first_relevant_rank": first,
        "source_recall": round(len(found) / len(expected), 3) if expected else None,
        "sources_found": found,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tests", type=Path, default=Path(__file__).resolve().parents[1] / "tests" / "test_queries.json")
    ap.add_argument("--top-k", type=int, default=None)
    ap.add_argument("--out", type=Path, default=PROJECT_ROOT / "reports")
    args = ap.parse_args()
    logging.basicConfig(level=logging.WARNING)

    tests = json.loads(args.tests.read_text())["queries"]
    llm = get_llm().describe()
    rows = []
    for t in tests:
        r = answer_question(t["question"], top_k=args.top_k)
        ret = score_retrieval(r["evidence"], t["expected_sources"]) if t["expected_sources"] else {}
        abstained = r["status"] == "insufficient" or bool(r["retrieval"]["missing_entities"])
        rows.append({
            "test": t,
            "status": r["status"],
            "status_ok": r["status"] in t["expected_status"],
            "abstained": abstained,
            "gate_passed": r["retrieval"]["sufficient"],
            "best_dense": r["retrieval"]["best_dense_score"],
            "missing_entities": r["retrieval"]["missing_entities"],
            "retrieval": ret,
            "answer": r["answer"],
            "generation": r["generation"],
            "timings_ms": r["timings_ms"],
            "evidence": [{
                "id": e["evidence_id"], "document": e["metadata"]["document_name"], "file": e["metadata"]["source_file"],
                "locator": e["metadata"]["locator"], "section": e["metadata"]["section"], "relevance": e["relevance"],
                "dense": e["dense_score"], "bm25": e["keyword_score"], "cited": e["cited"],
            } for e in r["evidence"]],
        })
        print(f"{t['id']:3} {r['status']:12} hit={ret.get('hit', '-')!s:5} rr={ret.get('reciprocal_rank', '-')!s:5} "
              f"dense={r['retrieval']['best_dense_score']:.3f}  {t['question'][:70]}")

    scored = [x for x in rows if x["retrieval"]]
    abst = [x for x in rows if x["test"].get("expect_abstain")]
    summary = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "llm": llm,
        "queries": len(rows),
        "hit_at_k": round(sum(x["retrieval"]["hit"] for x in scored) / len(scored), 3) if scored else None,
        "mrr": round(sum(x["retrieval"]["reciprocal_rank"] for x in scored) / len(scored), 3) if scored else None,
        "mean_source_recall": round(sum(x["retrieval"]["source_recall"] for x in scored) / len(scored), 3) if scored else None,
        "abstention_rate_on_out_of_scope": round(sum(x["abstained"] for x in abst) / len(abst), 3) if abst else None,
        "status_match_rate": round(sum(x["status_ok"] for x in rows) / len(rows), 3),
        "mean_latency_ms": round(sum(x["timings_ms"]["total"] for x in rows) / len(rows), 1),
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "test_report.json").write_text(json.dumps({"summary": summary, "results": rows}, indent=2, ensure_ascii=False))

    md = ["# RAG test report", "",
          f"Run: {summary['run_at']}  ", f"Answer engine: {llm['provider']} / {llm['model']}", "",
          "| Metric | Value |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in summary.items() if k not in ("run_at", "llm")]
    md += ["", "Hit@k / MRR / source recall are computed on queries with expected sources; "
           "abstention rate on the out-of-scope queries (status 'insufficient' or a question entity absent from the corpus).", ""]
    for x in rows:
        t = x["test"]
        md += [f"## {t['id']} ({t['category']}): {t['question']}", ""]
        if t.get("note"):
            md += [f"_Note: {t['note']}_", ""]
        md += [f"**Status:** {x['status']} (expected {' / '.join(t['expected_status'])}) | "
               f"best vector cosine {x['best_dense']} | relevance gate {'passed' if x['gate_passed'] else 'blocked'}"
               + (f" | absent from corpus: {', '.join(x['missing_entities'])}" if x['missing_entities'] else ""), ""]
        if x["retrieval"]:
            rr = x["retrieval"]
            md += [f"**Retrieval:** hit={rr['hit']}, first relevant rank={rr['first_relevant_rank']}, "
                   f"source recall={rr['source_recall']} (expected {', '.join(t['expected_sources'])})", ""]
        md += ["**Answer:**", "", "> " + x["answer"].replace("\n", "\n> "), "", "**Retrieved sources:**", "",
               "| # | Document | Location | Section | Relevance | Vector | BM25 | Cited |", "|---|---|---|---|---|---|---|---|"]
        for e in x["evidence"]:
            md.append(f"| {e['id']} | {e['document']} | {e['locator']} | {(e['section'] or '')[:50]} | {e['relevance']:.2f} | "
                      f"{e['dense'] if e['dense'] is not None else '–'} | {e['bm25'] if e['bm25'] is not None else '–'} | {'yes' if e['cited'] else ''} |")
        md.append("")
    (args.out / "test_report.md").write_text("\n".join(md), encoding="utf-8")
    print("\nSUMMARY", json.dumps(summary, indent=2))
    print(f"Report: {args.out / 'test_report.md'}")


if __name__ == "__main__":
    main()
