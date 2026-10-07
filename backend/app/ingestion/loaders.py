"""Recursive discovery and loading of PDF / Excel source files."""
from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path

import pandas as pd
import pymupdf

from .models import PageText, SourceDocument

log = logging.getLogger(__name__)

PDF_EXT = {".pdf"}
EXCEL_EXT = {".xlsx", ".xlsm", ".xls", ".csv"}
META_OVERRIDE_FILE = "_document_meta.json"
_STOP_END = {"on", "of", "for", "the", "and", "in", "to", "a", "an"}


# --------------------------------------------------------------------------
# discovery
# --------------------------------------------------------------------------
def discover_files(data_dir: Path) -> list[Path]:
    """All supported files under data_dir (recursive), skipping temp/hidden files."""
    files = []
    for p in sorted(data_dir.rglob("*")):
        if not p.is_file() or p.name.startswith((".", "~$", "_")):
            continue
        if p.suffix.lower() in PDF_EXT | EXCEL_EXT:
            files.append(p)
    return files


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_overrides(data_dir: Path) -> dict:
    """Optional user-editable display metadata (data/_document_meta.json)."""
    p = data_dir / META_OVERRIDE_FILE
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            log.warning("Could not parse %s: %s", p, e)
    return {}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _smart_title(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip(" -–:")
    if s.isupper():
        small = {"of", "and", "on", "in", "the", "for", "to", "a"}
        words = s.lower().split()
        s = " ".join(w if (i and w in small) else w[:1].upper() + w[1:] for i, w in enumerate(words))
    return s


def _name_from_filename(path: Path) -> str:
    stem = re.sub(r"[_\-]+", " ", path.stem)
    return _smart_title(stem.title() if stem.islower() else stem)


def infer_document_type(text: str, file_type: str, is_catalog: bool = False) -> str:
    if file_type == "excel":
        return "seismic_catalog" if is_catalog else "spreadsheet"
    t = text.lower()
    if "be it enacted by parliament" in t or re.search(r"\bact,? \d{4}\b", t[:3000]) and "chapter" in t:
        return "legislation"
    if "standard operating procedure" in t[:5000]:
        return "standard_operating_procedure"
    if "guideline" in t[:3000]:
        return "guidelines"
    if any(k in t[:6000] for k in ("report", "reconstruction strategy", "assessment", "study")):
        return "report"
    return "document"


def pdf_title(doc: "pymupdf.Document") -> str | None:
    """Title from PDF metadata or the largest-font text on page 1."""
    meta = (doc.metadata or {}).get("title", "") or ""
    if len(meta) > 6 and not meta.lower().startswith(("microsoft", "untitled")):
        return _smart_title(meta)
    if len(doc) == 0:
        return None
    spans = []
    for b in doc[0].get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            for s in line["spans"]:
                txt = s["text"].strip()
                if len(txt) > 1:
                    spans.append((s["size"], txt))
    if not spans:
        return None
    biggest = max(sz for sz, _ in spans)
    parts: list[str] = []
    for sz, txt in spans:
        if sz >= biggest * 0.92 and txt not in parts:
            parts.append(txt)
    title = _smart_title(" ".join(parts))
    if len(title) < 6 or len(title) > 160:
        return None
    if title.split()[-1].lower() in _STOP_END:   # e.g. "Standard Operating Procedure on" (rest is an image)
        return None
    return title


# --------------------------------------------------------------------------
# loaders
# --------------------------------------------------------------------------
def load_pdf(path: Path, rel: str, sha: str, override: dict) -> SourceDocument:
    doc = pymupdf.open(path)
    pages = [PageText(page=i + 1, text=p.get_text("text")) for i, p in enumerate(doc)]
    empty = [p.page for p in pages if len(p.text.strip()) < 30]
    full = "\n".join(p.text for p in pages)
    name = override.get("document_name") or pdf_title(doc) or _name_from_filename(path)
    sd = SourceDocument(
        source_file=rel,
        file_type="pdf",
        document_name=name,
        document_type=override.get("document_type") or infer_document_type(full, "pdf"),
        sha256=sha,
        pages=pages,
        extra={"page_count": len(pages), "pdf_metadata": {k: v for k, v in (doc.metadata or {}).items() if v}},
    )
    if empty:
        sd.warnings.append(
            f"{len(empty)} page(s) without extractable text (likely scanned images/figures; OCR not enabled): {empty}"
        )
    return sd


def _detect_header_row(raw: pd.DataFrame, scan: int = 15) -> int:
    """First row where most cells are non-empty short strings -> header row."""
    for i in range(min(scan, len(raw))):
        row = raw.iloc[i]
        vals = [v for v in row.tolist() if isinstance(v, str) and v.strip()]
        if len(vals) >= max(2, int(0.6 * raw.shape[1])) and all(len(v) < 60 for v in vals):
            return i
    return 0


def load_excel(path: Path, rel: str, sha: str, override: dict) -> SourceDocument:
    if path.suffix.lower() == ".csv":
        raw_sheets = {"csv": pd.read_csv(path, header=None, dtype=object)}
    else:
        raw_sheets = pd.read_excel(path, sheet_name=None, header=None, dtype=object)
    sheets: dict[str, pd.DataFrame] = {}
    titles: dict[str, str] = {}
    header_rows: dict[str, int] = {}
    for sheet, raw in raw_sheets.items():
        raw = raw.dropna(how="all").dropna(axis=1, how="all")
        if raw.empty:
            continue
        h = _detect_header_row(raw)
        # Any non-empty rows above the header are treated as a sheet title.
        above = [str(v).strip() for r in raw.iloc[:h].itertuples(index=False) for v in r if isinstance(v, str) and v.strip()]
        titles[sheet] = " ".join(above)
        df = raw.iloc[h + 1:].copy()
        df.columns = [str(c).strip() if pd.notna(c) else f"col_{j}" for j, c in enumerate(raw.iloc[h].tolist())]
        df["__excel_row__"] = [int(ix) + 1 for ix in df.index]  # 1-based Excel row number
        sheets[sheet] = df.reset_index(drop=True)
        header_rows[sheet] = h + 1
    first_title = next((t for t in titles.values() if t), "")
    name = override.get("document_name") or (_smart_title(first_title) if first_title else _name_from_filename(path))
    return SourceDocument(
        source_file=rel,
        file_type="excel",
        document_name=name,
        document_type=override.get("document_type") or "spreadsheet",  # refined by the chunker
        sha256=sha,
        sheets=sheets,
        extra={"sheet_titles": titles, "header_rows": header_rows},
    )


def load_file(path: Path, data_dir: Path, overrides: dict | None = None) -> SourceDocument:
    rel = path.relative_to(data_dir).as_posix()
    overrides = overrides or {}
    override = overrides.get(rel) or overrides.get(path.name) or {}
    sha = file_sha256(path)
    if path.suffix.lower() in PDF_EXT:
        return load_pdf(path, rel, sha, override)
    return load_excel(path, rel, sha, override)
