# India Earthquake RAG – basic prototype

Evidence-grounded question answering over an Indian earthquake / disaster-management corpus,
following the basic RAG flow of the reference paper (IEEE Access 2025, *AI-Driven Post-Earthquake
Emergency Material Demand Prediction: Integrating RAG With Reasoning LLM*):

```
DATA → CHUNKS → EMBEDDINGS → QDRANT → HYBRID RETRIEVAL (vector + BM25) → LLM → GROUNDED ANSWER → UI
```

Only the basic RAG layer is implemented. Casualty prediction, material-demand prediction, agents,
knowledge graphs and real-time feeds are intentionally out of scope; the module boundaries leave room for them.

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env              # optional: add ANTHROPIC_API_KEY (or an OpenAI-compatible endpoint)

cd backend
python -m scripts.ingest          # builds the index from ../data (incremental on re-runs)
uvicorn app.api.main:app --port 8000

# frontend (dev mode, proxies /api to :8000)
cd ../frontend && npm install && npm run dev      # http://localhost:5173
# or build once and let FastAPI serve it at http://localhost:8000
npm run build
```

Tests:

```bash
cd backend
python -m pytest -q               # unit tests (cleaning, headings, parsing, fusion, citations)
python -m scripts.run_tests       # 17 end-to-end test queries -> reports/test_report.md
```

> Embedded Qdrant locks its folder: stop the API before running `scripts.ingest` / `scripts.run_tests`
> from the command line, or use `POST /api/ingest`, or run a Qdrant server and set `QDRANT_URL`.

## Without an LLM key

With no LLM configured the system runs in **extractive mode**: retrieval is identical, and the answer
section shows the best-matching evidence sentences verbatim with citations, clearly labelled as excerpts.
Set `ANTHROPIC_API_KEY` (default model `claude-sonnet-5-5`) or `OPENAI_BASE_URL` + `LLM_MODEL`
(OpenAI, Ollama, vLLM, LM Studio…) for synthesised, cited answers.

## Adding documents

Drop PDF / Excel / CSV files anywhere under `data/` (sub-folders are scanned recursively, e.g.
`data/isro_earthquake/`, `data/PCA_Gujarat/`) and run `python -m scripts.ingest` again.
New files are added, changed files re-indexed, deleted files removed, unchanged files skipped
(tracked by SHA-256 in `storage/manifest.json`). `--rebuild` re-indexes everything.
`data/_document_meta.json` optionally overrides display names when a PDF's title cannot be extracted.

## How it works

| Stage | Module | What it does |
|---|---|---|
| Ingestion | `app/ingestion/loaders.py` | Recursive scan; PyMuPDF text per page; pandas per sheet with header-row detection; title and document-type inference; warns about pages without extractable text (scans need OCR, not enabled). |
| Cleaning | `app/ingestion/cleaning.py` | Unicode normalisation, page numbers, punctuation-only lines, running headers/footers, hyphenation repair, paragraph re-flow. |
| Chunking | `app/ingestion/chunking.py` | **PDF:** section-aware (chapters, legal sections `44. …—`, numbered headings, sub-headings, caps headings), ~1,000-char chunks, sentence overlap, never mixing sections unless tiny. **Excel catalogue:** an overview chunk, a computed summary per region (counts, period, magnitude stats, strongest events, events per year) and event listings of 10 rows per region. Generic sheets fall back to row windows. |
| Metadata | every chunk | `document_name, source_file, file_type, document_type, page_start/page_end/pages` or `sheet/row_start/row_end`, `locator`, `section`, `locations`, `topics`, `chunk_kind`, `file_sha256`, `ingested_at`. |
| Embeddings | `app/index/embeddings.py` | FastEmbed ONNX `BAAI/bge-small-en-v1.5` (384-d, CPU). Each chunk is embedded with a short context header (document, page/sheet, section, locations). |
| Vector DB | `app/index/vector_store.py` | Qdrant (embedded on disk by default, server via `QDRANT_URL`), cosine distance, full text + metadata in the payload, deterministic UUID point ids. |
| Keyword | `app/index/keyword.py` | BM25 (rank-bm25) rebuilt from Qdrant payloads at start-up and after ingestion; also detects query terms absent from the corpus. |
| Query | `app/retrieval/query.py` | Abbreviation expansion (NDRF, NDMA, DM Act…), filler removal for the keyword query, entity extraction, optional LLM rewrite (`QUERY_REWRITE=llm`). |
| Hybrid | `app/retrieval/hybrid.py` | Top-30 vector + top-30 BM25 → reciprocal rank fusion (k=60) → per-source / per-section caps for diversity → top-8 evidence with vector, BM25 and fused scores. A relevance gate (best cosine < 0.60) marks out-of-scope questions. |
| Generation | `app/generation/` | Evidence-only system prompt, `[E#]` citations required, JSON output with `answered / partial / insufficient`; invalid citations stripped; uncited answers downgraded; LLM never called when the gate fails. |
| API | `app/api/main.py` | `POST /api/ask`, `GET /api/health`, `GET /api/corpus`, `GET /api/examples`, `POST /api/ingest`. |
| UI | `frontend/` | React + Vite: question box, example questions, seismic-trace loading state, answer brief with status and clickable citations, evidence rail with document, page/sheet rows, section, relevance bar, vector and BM25 scores, cited markers; empty, error and insufficient-evidence states. |
| Logging | `logs/queries.jsonl` | Every query with retrieval results, scores, sources, status and per-stage latency – ready for MRR / relevance / faithfulness evaluation. |

## Current corpus (as provided)

| File | Indexed as | Passages |
|---|---|---|
| `DM-Act-2005.pdf` | The Disaster Management Act, 2005 (legislation) | 166 |
| `Eartrhquake.pdf` | NDRF Standard Operating Procedure on Earthquake | 66 |
| `earthquake-sikkireco.pdf` | Sikkim Earthquake (2011) – Reconstruction Strategy (NIDM report) | 103 |
| `Official Website of National Center of Seismology 1.xlsx` | NCS earthquake catalogue, 10,000 events, Feb 2016 – Dec 2024 | 1,081 |

The project brief also lists `isro_earthquake/`, `PCA_Gujarat/`, `KUTCH 2001.pdf`, `earthquake-mizo.pdf`
and `earthquake-sikki.pdf`; they were not among the files provided, so questions about them (e.g. ISRO data,
the 2001 Gujarat earthquake) are correctly reported as insufficient or partial until those files are added to `data/`.
Ten image-only pages of the Sikkim report (pp. 44–53) and one page of the NDRF SOP have no extractable text.
