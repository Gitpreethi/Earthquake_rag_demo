"""Shared data structures for the ingestion pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PageText:
    """Raw text of one PDF page (1-based page number)."""

    page: int
    text: str


@dataclass
class SourceDocument:
    """A loaded source file, before chunking."""

    source_file: str            # path relative to the data dir
    file_type: str              # pdf | excel
    document_name: str          # human readable title
    document_type: str          # legislation | sop | report | seismic_catalog | ...
    sha256: str
    pages: list[PageText] = field(default_factory=list)        # PDFs
    sheets: dict[str, Any] = field(default_factory=dict)        # Excel: sheet -> DataFrame
    extra: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


@dataclass
class Chunk:
    chunk_id: str               # deterministic UUID (used as Qdrant point id)
    text: str                   # clean chunk text shown to users / the LLM
    embed_text: str             # text actually embedded / keyword-indexed (with context header)
    metadata: dict[str, Any]
