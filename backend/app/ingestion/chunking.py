"""Section-aware chunking for PDFs and structure-aware chunking for Excel.

Every chunk carries traceable metadata (document, source file, page or
sheet/rows, section, document type, location and topic tags).
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pandas as pd

from ..config import settings
from .cleaning import clean_lines, find_repeated_lines, is_low_information, lines_to_paragraphs
from .enrichment import canonical_region, dominant_locations, tag_locations, tag_topics
from .models import Chunk, SourceDocument

NAMESPACE = uuid.UUID("5d1c1b8e-6f0e-4b7a-9d55-3b8f2a8c6e01")

# ---------------------------------------------------------------- headings
_CHAPTER = re.compile(r"^CHAPTER\s+([IVXLC]+|\d+)\b\.?\s*(.*)$", re.IGNORECASE)
_LEGAL_SECTION = re.compile(r"^(?:\d?\[)?(\d{1,3}[A-Z]{0,2})\.\s+([A-Z][^—]{2,140}?)\.?\s?—")
_NUM_CAPS = re.compile(r"^(\d{1,2})\.\s*([A-Z][A-Z0-9 &/,'()–\-]{3,90}?)\s*:?$")
_SUB_NUM = re.compile(r"^(\d{1,2}\.\d{1,2})\s+([A-Z][^.:]{2,70}):?$")


def _is_caps_heading(line: str) -> bool:
    if not (5 <= len(line) <= 90) or line.endswith(","):
        return False
    letters = [c for c in line if c.isalpha()]
    if len(letters) < 4:
        return False
    upper_ratio = sum(c.isupper() for c in letters) / len(letters)
    return upper_ratio > 0.85 and any(len(w) >= 4 for w in re.findall(r"[A-Za-z]+", line))


def detect_heading(line: str, next_line: str | None = None) -> tuple[int, str] | None:
    """Return (level, title) if the line is a heading. level 0=chapter, 1=section, 2=sub."""
    m = _CHAPTER.match(line)
    if m:
        rest = m.group(2).strip()
        if not rest and next_line and _is_caps_heading(next_line):
            rest = next_line
        return 0, f"Chapter {m.group(1).upper()}" + (f" – {rest.title()}" if rest else "")
    m = _LEGAL_SECTION.match(line)
    if m:
        return 1, f"Section {m.group(1)}. {m.group(2).strip()}"
    m = _NUM_CAPS.match(line)
    if m:
        return 1, f"{m.group(1)}. {m.group(2).strip().title()}"
    m = _SUB_NUM.match(line)
    if m:
        return 2, f"{m.group(1)} {m.group(2).strip()}"
    if _is_caps_heading(line):
        return 1, line.title()
    return None


# ---------------------------------------------------------------- helpers
@dataclass
class _Section:
    chapter: str | None
    title: str | None
    sub: str | None
    units: list[tuple[int, str]] = field(default_factory=list)  # (page, paragraph)

    @property
    def path(self) -> str:
        return " › ".join(p for p in (self.chapter, self.title, self.sub) if p)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.;:!?])\s+(?=[A-Z(\"'•\d])", text)
    return [p for p in parts if p.strip()]


def _tail_overlap(text: str, n: int) -> str:
    if n <= 0 or len(text) <= n:
        return ""
    sents = _split_sentences(text)
    out = ""
    for s in reversed(sents):
        if len(out) + len(s) > n:
            break
        out = f"{s} {out}".strip()
    return out


def _chunk_id(source_file: str, idx: int, text: str) -> str:
    return str(uuid.uuid5(NAMESPACE, f"{source_file}::{idx}::{text[:200]}"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _embed_header(doc_name: str, locator: str, section: str | None, locations: list[str]) -> str:
    bits = [doc_name, locator]
    if section:
        bits.append(section)
    if locations:
        bits.append("Locations: " + ", ".join(locations[:5]))
    return " | ".join(bits)


# ---------------------------------------------------------------- PDF
def chunk_pdf(doc: SourceDocument) -> list[Chunk]:
    target, max_c = settings.chunk_target_chars, settings.chunk_max_chars
    min_c, overlap = settings.chunk_min_chars, settings.chunk_overlap_chars

    repeated = find_repeated_lines(doc.pages)
    sections: list[_Section] = [_Section(None, None, None)]
    chapter = title = sub = None

    for page in doc.pages:
        lines = clean_lines(page.text, repeated)
        page_buf: list[str] = []

        def flush_page_buf():
            for para in lines_to_paragraphs(page_buf):
                sections[-1].units.append((page.page, para))
            page_buf.clear()

        skip_next = False
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            nxt = lines[i + 1] if i + 1 < len(lines) else None
            h = detect_heading(line, nxt)
            if h is None:
                page_buf.append(line)
                continue
            flush_page_buf()
            level, htitle = h
            if level == 0:
                chapter, title, sub = htitle, None, None
                if nxt and _is_caps_heading(nxt) and nxt.title() in htitle:
                    skip_next = True
            elif level == 1:
                title, sub = htitle, None
            else:
                sub = htitle
            sections.append(_Section(chapter, title, sub))
            # Legal sections carry body text on the same line – keep it.
            if level == 1 and _LEGAL_SECTION.match(line):
                page_buf.append(line)
        flush_page_buf()

    # --- pack paragraphs into chunks -----------------------------------
    raw_chunks: list[dict] = []
    cur_text, cur_pages, cur_sections = "", [], []

    def emit():
        nonlocal cur_text, cur_pages, cur_sections
        if cur_text.strip():
            raw_chunks.append({"text": cur_text.strip(), "pages": sorted(set(cur_pages)), "sections": list(dict.fromkeys(cur_sections))})
        cur_text, cur_pages, cur_sections = "", [], []

    for sec in sections:
        if not sec.units:
            continue
        # section boundary: close the running chunk if it is big enough
        if cur_text and len(cur_text) >= min_c:
            emit()
        for pg, para in sec.units:
            pieces = [para] if len(para) <= max_c else _split_sentences(para)
            for piece in pieces:
                if cur_text and len(cur_text) + len(piece) + 1 > target and len(cur_text) >= min_c:
                    carry = _tail_overlap(cur_text, overlap)
                    carry_pages = cur_pages[-1:] if carry else []
                    emit()
                    cur_text, cur_pages = carry, carry_pages
                    cur_sections = [sec.path] if sec.path else []
                cur_text = f"{cur_text}\n{piece}" if cur_text else piece
                cur_pages.append(pg)
                if sec.path:
                    cur_sections.append(sec.path)
    emit()

    doc_locs = dominant_locations([c["text"] for c in raw_chunks])
    chunks: list[Chunk] = []
    for c in raw_chunks:
        text = c["text"]
        if len(text) < 40 or is_low_information(text):
            continue
        idx = len(chunks)
        pages = c["pages"]
        section = c["sections"][0] if c["sections"] else None
        locs = tag_locations(text)
        locator = f"p. {pages[0]}" if len(pages) == 1 else f"pp. {pages[0]}–{pages[-1]}"
        meta = {
            "document_name": doc.document_name,
            "source_file": doc.source_file,
            "file_type": doc.file_type,
            "document_type": doc.document_type,
            "page_start": pages[0],
            "page_end": pages[-1],
            "pages": pages,
            "sheet": None,
            "row_start": None,
            "row_end": None,
            "locator": locator,
            "section": section,
            "sections": c["sections"][:5],
            "locations": locs,
            "document_locations": doc_locs,
            "topics": tag_topics(text),
            "chunk_index": idx,
            "chunk_kind": "text",
            "char_count": len(text),
            "file_sha256": doc.sha256,
            "ingested_at": _now(),
        }
        header = _embed_header(doc.document_name, locator, section, locs or doc_locs)
        chunks.append(Chunk(_chunk_id(doc.source_file, idx, text), text, f"{header}\n{text}", meta))
    return chunks


# ---------------------------------------------------------------- Excel
def _find_col(cols: list[str], *keys: str) -> str | None:
    for k in keys:
        for c in cols:
            if k in c.lower():
                return c
    return None


_MAG = re.compile(r"(-?\d+(?:\.\d+)?)\s*(?:\[([A-Za-z]+)\])?")


def parse_magnitude(v) -> tuple[float | None, str | None]:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None, None
    m = _MAG.search(str(v))
    if not m:
        return None, None
    return float(m.group(1)), m.group(2)


def parse_place(loc: str) -> tuple[str, str]:
    """'26km NW of Uttarkashi, Uttarakhand, India' -> ('Uttarakhand', 'India')."""
    s = str(loc or "").strip()
    s = re.split(r"\bof\b", s, maxsplit=1)[-1] if re.search(r"\d+\s*km", s) else s
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return "Unknown", "Unknown"
    country = parts[-1]
    if country.lower() == "india":
        if len(parts) >= 2:
            raw = parts[-2]
            return canonical_region(raw) or raw.title(), "India"
        return "India (unspecified)", "India"
    canon = canonical_region(country)
    return canon or country, country


def _fmt_event(r: pd.Series, c: dict) -> str:
    bits = []
    if c["time"]:
        bits.append(str(r[c["time"]]))
    if r["_mag"] is not None:
        bits.append(f"M{r['_mag']:.1f}" + (f" ({r['_scale']})" if r["_scale"] else ""))
    if c["depth"] and pd.notna(r[c["depth"]]):
        bits.append(f"depth {r[c['depth']]} km")
    if c["lat"] and c["lon"] and pd.notna(r[c["lat"]]):
        bits.append(f"lat {r[c['lat']]}, lon {r[c['lon']]}")
    if c["loc"]:
        bits.append(str(r[c["loc"]]))
    return " | ".join(bits)


def _mk_excel_chunk(doc, idx, text, sheet, rows, region, kind, topics, locs) -> Chunk:
    row_start, row_end = (min(rows), max(rows)) if rows else (None, None)
    locator = f"Sheet '{sheet}'" + (f", rows {row_start}–{row_end}" if rows and kind == "events" else (f", {len(rows)} rows summarised" if rows else ""))
    meta = {
        "document_name": doc.document_name,
        "source_file": doc.source_file,
        "file_type": doc.file_type,
        "document_type": doc.document_type,
        "page_start": None,
        "page_end": None,
        "pages": [],
        "sheet": sheet,
        "row_start": row_start,
        "row_end": row_end,
        "locator": locator,
        "section": region,
        "sections": [region] if region else [],
        "locations": locs,
        "document_locations": [],
        "topics": topics,
        "chunk_index": idx,
        "chunk_kind": kind,
        "char_count": len(text),
        "file_sha256": doc.sha256,
        "ingested_at": _now(),
    }
    header = _embed_header(doc.document_name, locator, region, locs)
    return Chunk(_chunk_id(doc.source_file, idx, text), text, f"{header}\n{text}", meta)


def _region_summary(region: str, country: str, g: pd.DataFrame, c: dict, src_name: str) -> str:
    mags = g["_mag"].dropna()
    lines = [f"Earthquake catalogue summary for {region}" + (f" ({country})" if country not in (region, "Unknown") else "") + f" – source: {src_name}."]
    lines.append(f"Recorded events: {len(g)}.")
    if c["time"]:
        lines.append(f"Period covered: {g['_t'].min()} to {g['_t'].max()}.")
    if len(mags):
        lines.append(
            f"Magnitude range M{mags.min():.1f}–M{mags.max():.1f} (mean M{mags.mean():.2f}); "
            f"events M≥4.0: {(mags >= 4).sum()}, M≥5.0: {(mags >= 5).sum()}, M≥6.0: {(mags >= 6).sum()}."
        )
    if c["depth"]:
        d = pd.to_numeric(g[c["depth"]], errors="coerce").dropna()
        if len(d):
            lines.append(f"Focal depth range {d.min():g}–{d.max():g} km (median {d.median():g} km).")
    if c["time"]:
        years = g["_t"].dt.year.value_counts().sort_index()
        if len(years):
            lines.append("Events per year: " + ", ".join(f"{int(y)}: {n}" for y, n in years.items()) + ".")
    top = g.sort_values("_mag", ascending=False).head(5)
    if len(top):
        lines.append("Strongest recorded events:")
        lines += [f"- {_fmt_event(r, c)}" for _, r in top.iterrows()]
    return "\n".join(lines)


def chunk_excel(doc: SourceDocument) -> list[Chunk]:
    chunks: list[Chunk] = []
    n_rows = settings.excel_rows_per_chunk
    for sheet, df in doc.sheets.items():
        cols = [c for c in df.columns if c != "__excel_row__"]
        c = {
            "time": _find_col(cols, "origin time", "time", "date"),
            "mag": _find_col(cols, "magnitude", "mag"),
            "lat": _find_col(cols, "lat"),
            "lon": _find_col(cols, "long", "lon"),
            "depth": _find_col(cols, "depth"),
            "loc": _find_col(cols, "location", "place", "region"),
        }
        is_catalog = bool(c["mag"] and c["loc"])
        if not is_catalog:
            # generic tabular fallback: windows of rows rendered as key: value
            for start in range(0, len(df), n_rows):
                w = df.iloc[start:start + n_rows]
                text = "\n".join("; ".join(f"{k}: {v}" for k, v in r.items() if k != "__excel_row__" and pd.notna(v)) for _, r in w.iterrows())
                if text.strip():
                    chunks.append(_mk_excel_chunk(doc, len(chunks), text, sheet, w["__excel_row__"].tolist(), None, "rows", tag_topics(text), tag_locations(text)))
            continue

        doc.document_type = "seismic_catalog"
        df = df.copy()
        parsed = df[c["mag"]].map(parse_magnitude)
        df["_mag"] = parsed.map(lambda x: x[0])
        df["_scale"] = parsed.map(lambda x: x[1])
        places = df[c["loc"]].map(parse_place)
        df["_region"] = places.map(lambda x: x[0])
        df["_country"] = places.map(lambda x: x[1])
        if c["time"]:
            df["_t"] = pd.to_datetime(df[c["time"]].astype(str).str.replace(r"\s*IST$", "", regex=True), errors="coerce")
        src = doc.document_name
        topics = ["seismology_hazard"]

        # (a) sheet overview
        mags = df["_mag"].dropna()
        by_region = df.groupby(["_region", "_country"]).size().sort_values(ascending=False)
        india = df[df["_country"] == "India"]
        ov = [f"Overview of the earthquake catalogue '{src}' (sheet '{sheet}').",
              f"Total recorded events: {len(df)}; events located in India: {len(india)}; outside India: {len(df) - len(india)}."]
        if c["time"]:
            ov.append(f"Period covered: {df['_t'].min()} to {df['_t'].max()}.")
        if len(mags):
            ov.append(f"Magnitude range M{mags.min():.1f}–M{mags.max():.1f}; events M≥5.0: {(mags >= 5).sum()}, M≥6.0: {(mags >= 6).sum()}.")
        ov.append("Columns: " + ", ".join(cols) + ".")
        ov.append("Regions with most events: " + "; ".join(f"{r} ({n})" for (r, _), n in by_region.head(12).items()) + ".")
        ov.append("Strongest events in the catalogue:")
        ov += [f"- {_fmt_event(r, c)}" for _, r in df.sort_values("_mag", ascending=False).head(6).iterrows()]
        ov.append("Strongest events located in India:")
        ov += [f"- {_fmt_event(r, c)}" for _, r in india.sort_values("_mag", ascending=False).head(6).iterrows()]
        text = "\n".join(ov)
        chunks.append(_mk_excel_chunk(doc, len(chunks), text, sheet, df["__excel_row__"].tolist(), "Catalogue overview", "summary", topics, ["India"]))

        # (b) region summaries + (c) event listings
        for (region, country), g in df.groupby(["_region", "_country"], sort=False):
            g = g.sort_values("_t") if c["time"] else g
            locs = [region] if region not in ("Unknown",) else []
            text = _region_summary(region, country, g, c, src)
            chunks.append(_mk_excel_chunk(doc, len(chunks), text, sheet, g["__excel_row__"].tolist(), region, "summary", topics, locs))
            for start in range(0, len(g), n_rows):
                w = g.iloc[start:start + n_rows]
                head = f"Earthquake events recorded in {region}" + (f", {country}" if country not in (region, "Unknown") else "") + f" (events {start + 1}–{start + len(w)} of {len(g)}):"
                text = head + "\n" + "\n".join(f"- {_fmt_event(r, c)}" for _, r in w.iterrows())
                chunks.append(_mk_excel_chunk(doc, len(chunks), text, sheet, w["__excel_row__"].tolist(), region, "events", topics, locs))
    for ch in chunks:
        ch.metadata["document_type"] = doc.document_type
    return chunks


def chunk_document(doc: SourceDocument) -> list[Chunk]:
    return chunk_pdf(doc) if doc.file_type == "pdf" else chunk_excel(doc)
