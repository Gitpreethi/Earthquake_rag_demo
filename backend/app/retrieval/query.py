"""Turn a user question into retrieval queries.

* dense query  – the question with common abbreviations expanded
                 (the embedding model adds its own retrieval instruction)
* keyword query – content-bearing tokens only (question filler removed)
* optional LLM rewrite (QUERY_REWRITE=llm) for vaguer questions
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..index.keyword import stem, tokenize

# Domain abbreviations (general Indian disaster-management vocabulary).
ABBREVIATIONS = {
    r"\bDM Act\b": "Disaster Management Act",
    r"\bNDRF\b": "NDRF National Disaster Response Force",
    r"\bSDRF\b": "SDRF State Disaster Response Force",
    r"\bNDMA\b": "NDMA National Disaster Management Authority",
    r"\bSDMA\b": "SDMA State Disaster Management Authority",
    r"\bDDMA\b": "DDMA District Disaster Management Authority",
    r"\bNIDM\b": "NIDM National Institute of Disaster Management",
    r"\bNCS\b": "NCS National Center of Seismology",
    r"\bSOP\b": "SOP Standard Operating Procedure",
    r"\bUSAR\b": "USAR urban search and rescue",
    r"\bEOC\b": "EOC Emergency Operations Centre",
    r"\bIMD\b": "IMD India Meteorological Department",
}

# Words that describe the *request* rather than its subject.
FILLER = set(
    """information info available availability knowledge base kb document documents data dataset present contain contains
    summarize summarise summary tell explain describe details detail say says said give show list mention mentioned
    regarding related relevant please question answer anything something kind type""".split()
)
FILLER |= {stem(w) for w in FILLER}


@dataclass
class RetrievalQuery:
    original: str
    dense_text: str
    keyword_tokens: list[str]
    salient_tokens: list[str] = field(default_factory=list)  # used for "missing term" checks
    entity_terms: list[str] = field(default_factory=list)    # capitalised names / acronyms in the question
    rewritten_by_llm: bool = False

    def as_dict(self) -> dict:
        return {
            "original": self.original,
            "dense_query": self.dense_text,
            "keyword_query": " ".join(self.keyword_tokens),
            "rewritten_by_llm": self.rewritten_by_llm,
        }


def expand_abbreviations(text: str) -> str:
    for pat, rep in ABBREVIATIONS.items():
        text = re.sub(pat, rep, text)
    return text


def build_query(question: str, rewrite: str | None = None) -> RetrievalQuery:
    q = re.sub(r"\s+", " ", question).strip()
    base = rewrite or q
    expanded = expand_abbreviations(base)
    tokens = [t for t in tokenize(expanded) if t not in FILLER]
    if not tokens:                       # e.g. "what information is available?"
        tokens = tokenize(expanded)
    salient = [t for t in tokenize(q) if t not in FILLER and len(t) > 2]
    # Capitalised words that are not sentence-initial, plus acronyms (e.g. ISRO, Kutch)
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", q)
    entities = [w for i, w in enumerate(words) if (w.isupper() and len(w) >= 3) or (i > 0 and w[0].isupper())]
    entity_terms = list(dict.fromkeys(t for w in entities for t in tokenize(w)))
    return RetrievalQuery(original=q, dense_text=expanded, keyword_tokens=tokens, salient_tokens=salient,
                          entity_terms=entity_terms, rewritten_by_llm=bool(rewrite))
