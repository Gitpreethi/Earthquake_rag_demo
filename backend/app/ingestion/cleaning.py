"""Text cleaning for extracted PDF text.

Removes common extraction noise (page numbers, punctuation-only lines,
repeated running headers/footers, broken hyphenation) while keeping
line structure so headings can still be detected afterwards.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter

from .models import PageText

_PUNCT_ONLY = re.compile(r"^[\W_]+$", re.UNICODE)
_PAGE_NUM = re.compile(r"^(page\s*)?\(?\d{1,3}\)?$", re.IGNORECASE)
_ROMAN_PAGE = re.compile(r"^[ivxlc]{1,6}$", re.IGNORECASE)
_MULTISPACE = re.compile(r"[ \t ]+")
_SHORT_JUNK = re.compile(r"^[a-z]?[\.\),;:]?$", re.IGNORECASE)

_REPLACEMENTS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "–", "­": "", "ﬁ": "fi", "ﬂ": "fl", "": "•", "": "•",
}


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for a, b in _REPLACEMENTS.items():
        text = text.replace(a, b)
    return text


def _line_key(line: str) -> str:
    """Key used to detect running headers/footers (digits/punct ignored)."""
    return re.sub(r"[^a-z]+", " ", line.lower()).strip()


def find_repeated_lines(pages: list[PageText], min_ratio: float = 0.3, min_pages: int = 3) -> set[str]:
    """Lines that appear on many pages (running headers / footers)."""
    if len(pages) < min_pages:
        return set()
    counts: Counter[str] = Counter()
    for p in pages:
        keys = {_line_key(l) for l in p.text.splitlines() if 0 < len(l.strip()) < 120}
        counts.update(k for k in keys if len(k) >= 6)
    threshold = max(min_pages, int(len(pages) * min_ratio))
    return {k for k, c in counts.items() if c >= threshold}


def clean_lines(text: str, repeated: set[str] | None = None) -> list[str]:
    """Return cleaned, non-empty lines for one page."""
    repeated = repeated or set()
    text = normalise(text).replace("\t", " ")
    out: list[str] = []
    for raw in text.splitlines():
        line = _MULTISPACE.sub(" ", raw).strip()
        if not line:
            continue
        if _PUNCT_ONLY.match(line) or _PAGE_NUM.match(line) or _ROMAN_PAGE.match(line) or _SHORT_JUNK.match(line):
            continue
        key = _line_key(line)
        if key in repeated or any(key.startswith(r) and len(key) - len(r) < 25 for r in repeated):
            continue
        out.append(line)
    # re-join words broken by hyphenation at line end: "disas-" + "ter"
    joined: list[str] = []
    for line in out:
        if joined and re.search(r"[a-z]-$", joined[-1]) and re.match(r"^[a-z]", line):
            joined[-1] = joined[-1][:-1] + line
        else:
            joined.append(line)
    return joined


_BULLET = re.compile(r"^(•|-|–|\*|\(?[a-z]{1,3}\)|\(?[ivx]{1,5}\)|[a-z]\.|[ivx]{1,5}\.|\d{1,2}(\.\d{1,2})*\.?)\s")


def lines_to_paragraphs(lines: list[str]) -> list[str]:
    """Merge wrapped lines into paragraphs; keep bullets / numbered items separate."""
    paras: list[str] = []
    buf = ""
    for line in lines:
        starts_item = bool(_BULLET.match(line))
        if not buf:
            buf = line
            continue
        prev_ends = buf.rstrip().endswith((".", ":", ";", "?", "!"))
        if starts_item or (prev_ends and line[:1].isupper()):
            paras.append(buf)
            buf = line
        else:
            buf = f"{buf} {line}"
    if buf:
        paras.append(buf)
    return [p.strip() for p in paras if len(p.strip()) > 1]


def is_low_information(text: str) -> bool:
    """True for text that is mostly numbers/symbols (e.g. figure residue)."""
    letters = sum(ch.isalpha() for ch in text)
    return len(text) == 0 or letters / max(len(text), 1) < 0.45
