"""RAG orchestration: question -> retrieval query -> hybrid retrieval -> grounded answer."""
from __future__ import annotations

import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone

from ..config import settings
from ..index.keyword import tokenize
from ..retrieval.hybrid import RetrievalResult, retrieve
from .llm import BaseLLM, LLMError, get_llm
from .prompts import QUERY_REWRITE_PROMPT, SYSTEM_PROMPT, build_user_prompt

log = logging.getLogger(__name__)

INSUFFICIENT_MSG = (
    "The knowledge base does not contain enough evidence to answer this question. "
    "The closest retrieved passages are shown below for transparency, but none of them is relevant enough "
    "to support an answer."
)
_CITE = re.compile(r"\[(E\d+)\]")


# ------------------------------------------------------------------ helpers
def _parse_llm_json(raw: str) -> dict:
    """Extract the JSON object from an LLM reply (tolerates code fences / prose)."""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return {"status": "answered", "answer": raw.strip(), "used_evidence": [], "missing_information": "", "_unparsed": True}


def _validate_citations(answer: str, valid_ids: set[str]) -> tuple[str, list[str], list[str]]:
    """Drop citations to evidence ids that were not supplied; return (answer, cited, invalid)."""
    cited, invalid = [], []
    def repl(m):
        eid = m.group(1)
        if eid in valid_ids:
            cited.append(eid)
            return m.group(0)
        invalid.append(eid)
        return ""
    cleaned = _CITE.sub(repl, answer)
    cleaned = re.sub(r"[ \t]+([.,;:])", r"\1", cleaned)
    return cleaned, list(dict.fromkeys(cited)), invalid


def _split_sentences(text: str) -> list[str]:
    out = []
    for line in text.splitlines():           # list items / table rows stay separate
        out += re.split(r"(?<=[.;!?])\s+(?=[A-Z(•\-\d])", line)
    return [s.strip(" -•") for s in out if len(s.strip()) > 25]


def _display_terms(question: str, tokens: list[str]) -> list[str]:
    """Map stemmed tokens back to the words the user typed (e.g. 'isro' -> 'ISRO')."""
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]*", question)
    out = []
    for t in tokens:
        match = next((w for w in words if tokenize(w) == [t]), t)
        out.append(match)
    return out


def extractive_answer(question: str, result: RetrievalResult, max_items: int = 5) -> dict:
    """Offline fallback: best-matching sentence(s) from the top evidence, verbatim, with citations."""
    q_tokens = set(result.query.keyword_tokens)
    items = []
    for e in result.evidence:
        sents = _split_sentences(e.text) or [e.text[:300]]
        def score(s: str) -> float:
            overlap = len(q_tokens & set(tokenize(s)))
            # prefer informative sentences over headings / list intros
            return overlap * 2 + min(len(s), 220) / 110 - (1.5 if s.rstrip().endswith(":") else 0)
        scored = sorted(sents, key=lambda s: -score(s))
        best = scored[0]
        if len(q_tokens & set(tokenize(best))) == 0 and e.dense_score is None:
            continue
        items.append(f"- {best[:400]} [{e.evidence_id}]")
        if len(items) >= max_items:
            break
    # Extractive mode cannot judge completeness, so it never claims a full answer.
    status = "partial" if items else "insufficient"
    missing = ""
    if result.missing_entities:
        # The question names something (dataset, organisation, place) the corpus never mentions.
        status = "insufficient"
        missing = ("The knowledge base contains no passage mentioning: " + ", ".join(_display_terms(question, result.missing_entities))
                   + ". The sentences below are only related material, not an answer.")
    header = (
        "**Extractive mode** – no LLM is configured, so these are the most relevant sentences quoted verbatim "
        "from the retrieved evidence (not a synthesised answer):\n\n"
    )
    if missing:
        header = f"⚠ {missing}\n\n" + header
    answer = header + ("\n".join(items) if items else "No sentence in the retrieved evidence matches the question.")
    cited = [m for m in _CITE.findall(answer)]
    return {"status": status, "answer": answer, "used_evidence": list(dict.fromkeys(cited)), "missing_information": missing}


def _log_query(record: dict) -> None:
    try:
        settings.ensure_dirs()
        with (settings.log_dir / "queries.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # logging must never break answering
        log.exception("Could not write query log")


# ------------------------------------------------------------------ main entry point
def answer_question(question: str, top_k: int | None = None, llm: BaseLLM | None = None) -> dict:
    t_start = time.perf_counter()
    llm = llm or get_llm()
    question = question.strip()

    # 1) optional LLM query rewrite
    rewrite = None
    if settings.query_rewrite == "llm" and llm.is_generative:
        try:
            rewrite = llm.complete("You write search queries.", QUERY_REWRITE_PROMPT.format(question=question), 60).strip()
        except LLMError as e:
            log.warning("Query rewrite failed: %s", e)

    # 2) hybrid retrieval
    result = retrieve(question, top_k=top_k, rewrite=rewrite)
    valid_ids = {e.evidence_id for e in result.evidence}

    # 3) grounded generation
    t_gen = time.perf_counter()
    error = None
    invalid_citations: list[str] = []
    if not result.sufficient:
        gen = {"status": "insufficient", "answer": INSUFFICIENT_MSG, "used_evidence": [],
               "missing_information": "No retrieved passage reached the relevance threshold."}
        mode = "gate"            # LLM deliberately not called
    elif not llm.is_generative:
        gen = extractive_answer(question, result)
        mode = "extractive"
    else:
        try:
            raw = llm.complete(SYSTEM_PROMPT, build_user_prompt(question, result.evidence, _display_terms(question, result.missing_terms)))
            gen = _parse_llm_json(raw)
            ans, cited, invalid_citations = _validate_citations(str(gen.get("answer", "")), valid_ids)
            gen["answer"] = ans
            used = [u for u in (gen.get("used_evidence") or []) if u in valid_ids]
            gen["used_evidence"] = list(dict.fromkeys(cited + used))
            if gen.get("status") not in ("answered", "partial", "insufficient"):
                gen["status"] = "answered"
            # An answer without any valid citation is not verifiably grounded.
            if gen["status"] != "insufficient" and not gen["used_evidence"]:
                gen["status"] = "partial"
                gen["missing_information"] = (gen.get("missing_information") or "") + " (answer contained no valid evidence citations)"
            if result.missing_entities and gen["status"] == "answered":
                gen["status"] = "partial"
            mode = "llm"
        except LLMError as e:
            error = str(e)
            gen = extractive_answer(question, result)
            gen["answer"] = f"⚠ The LLM call failed ({e}). Falling back to extractive evidence.\n\n" + gen["answer"]
            mode = "extractive_fallback"
    t_end = time.perf_counter()

    used = set(gen.get("used_evidence") or [])
    evidence = []
    for e in result.evidence:
        d = e.to_dict()
        d["cited"] = e.evidence_id in used
        evidence.append(d)

    response = {
        "query_id": uuid.uuid4().hex[:12],
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "question": question,
        "rag_generated": True,
        "status": gen.get("status", "answered"),
        "answer": gen.get("answer", ""),
        "used_evidence": gen.get("used_evidence", []),
        "missing_information": (gen.get("missing_information") or "").strip(),
        "evidence": evidence,
        "retrieval": {
            **result.query.as_dict(),
            "method": "hybrid (dense cosine via Qdrant + BM25, reciprocal rank fusion)",
            "best_dense_score": result.best_dense_score,
            "min_dense_score": settings.min_dense_score,
            "sufficient": result.sufficient,
            "missing_terms": result.missing_terms,
            "missing_entities": _display_terms(question, result.missing_entities),
            "candidates": result.candidates,
        },
        "generation": {**llm.describe(), "mode": mode, "error": error, "invalid_citations_removed": invalid_citations},
        "timings_ms": {
            **result.timings_ms,
            "generation": round((t_end - t_gen) * 1000, 1),
            "total": round((t_end - t_start) * 1000, 1),
        },
    }
    _log_query({
        **{k: response[k] for k in ("query_id", "timestamp", "question", "status", "used_evidence", "timings_ms", "generation")},
        "retrieval": response["retrieval"],
        "evidence": [{k: e[k] for k in ("evidence_id", "chunk_id", "rank", "relevance", "dense_score", "keyword_score", "cited")}
                     | {"document_name": e["metadata"]["document_name"], "source_file": e["metadata"]["source_file"], "locator": e["metadata"]["locator"]}
                     for e in evidence],
        "answer": response["answer"],
    })
    return response
