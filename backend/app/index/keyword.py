"""Keyword (BM25) index built from the chunk payloads stored in Qdrant.

Qdrant is the single source of truth, so the BM25 index is rebuilt in
memory from its payloads at start-up and after every ingestion run.
"""
from __future__ import annotations

import re
import threading

import numpy as np
from rank_bm25 import BM25Okapi

STOPWORDS = set("""
a about above after again against all am an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers him his how i if
in into is it its itself just me more most my no nor not now of off on once only or other our out over own same she should
so some such than that the their them then there these they this those through to too under until up very was we were what
when where which while who whom why will with would you your yours shall may also etc per via within upon
""".split())

_TOKEN = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?")


def stem(tok: str) -> str:
    if tok.isdigit() or len(tok) <= 4:
        return tok
    for suf in ("ations", "ation", "ings", "ing", "ies", "ed"):
        if tok.endswith(suf) and len(tok) - len(suf) >= 4:
            return tok[: -len(suf)] + ("y" if suf == "ies" else "")
    if tok.endswith(("sses", "xes", "zes", "ches", "shes")):
        return tok[:-2]
    if tok.endswith("s") and not tok.endswith(("ss", "us", "is")):
        return tok[:-1]
    return tok


def tokenize(text: str) -> list[str]:
    return [stem(t) for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS and (len(t) > 1 or t.isdigit())]


class KeywordIndex:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.ids: list[str] = []
        self.payloads: list[dict] = []
        self.bm25: BM25Okapi | None = None
        self.doc_freq: dict[str, int] = {}

    def build(self, payloads: list[dict]) -> None:
        corpus = [tokenize(p.get("embed_text") or p.get("text", "")) for p in payloads]
        df: dict[str, int] = {}
        for toks in corpus:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        bm25 = BM25Okapi(corpus) if corpus else None
        with self._lock:
            self.ids = [p["id"] for p in payloads]
            self.payloads = payloads
            self.bm25 = bm25
            self.doc_freq = df

    def __len__(self) -> int:
        return len(self.ids)

    def search(self, query_tokens: list[str], limit: int) -> list[tuple[str, float, dict]]:
        with self._lock:
            if not self.bm25 or not query_tokens:
                return []
            scores = self.bm25.get_scores(query_tokens)
            order = np.argsort(-scores)[:limit]
            return [(self.ids[i], float(scores[i]), self.payloads[i]) for i in order if scores[i] > 0]

    def missing_terms(self, query_tokens: list[str]) -> list[str]:
        """Query terms that never occur in the knowledge base."""
        return [t for t in dict.fromkeys(query_tokens) if self.doc_freq.get(t, 0) == 0]


_index = KeywordIndex()


def get_keyword_index() -> KeywordIndex:
    return _index
