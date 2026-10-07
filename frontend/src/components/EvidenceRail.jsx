import React, { useEffect, useRef, useState } from "react";

const DOC_TYPE = {
  legislation: "Legislation",
  standard_operating_procedure: "Standard operating procedure",
  report: "Report",
  seismic_catalog: "Seismic event catalogue",
  guidelines: "Guidelines",
  spreadsheet: "Spreadsheet",
  document: "Document",
};

function EvidenceItem({ e, active, insufficient }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const m = e.metadata;

  useEffect(() => {
    if (active && ref.current) {
      setOpen(true);
      ref.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
      ref.current.focus({ preventScroll: true });
    }
  }, [active]);

  const where = m.sheet
    ? m.chunk_kind === "events"
      ? `Sheet ${m.sheet}, rows ${m.row_start}–${m.row_end}`
      : `Sheet ${m.sheet}, ${m.locator.split(", ").slice(1).join(", ") || "computed summary"}`
    : m.page_start === m.page_end
      ? `Page ${m.page_start}`
      : `Pages ${m.page_start}–${m.page_end}`;
  const pct = Math.round(e.relevance * 100);

  return (
    <li
      ref={ref}
      tabIndex={-1}
      id={`ev-${e.evidence_id}`}
      className={`ev ${e.cited ? "ev--cited" : ""} ${active ? "ev--active" : ""} ${insufficient ? "ev--weak" : ""}`}
    >
      <div className="ev__top">
        <span className="ev__id">{e.evidence_id}</span>
        <div className="ev__src">
          <p className="ev__doc">{m.document_name}</p>
          <p className="ev__where">
            {where}
            {m.section ? <span className="ev__section"> in {m.section}</span> : null}
          </p>
        </div>
        {e.cited && <span className="ev__cited">Cited</span>}
      </div>

      <div className="ev__score" title={`Fused relevance (reciprocal rank fusion), ${pct}% of maximum`}>
        <div className="meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={pct} aria-label="Relevance">
          <span style={{ width: `${pct}%` }} />
        </div>
        <span className="ev__pct">{pct}%</span>
      </div>
      <dl className="ev__nums">
        <div>
          <dt>Vector</dt>
          <dd>{e.dense_score != null ? `${e.dense_score.toFixed(3)} (#${e.dense_rank})` : "not matched"}</dd>
        </div>
        <div>
          <dt>Keyword</dt>
          <dd>{e.keyword_score != null ? `${e.keyword_score.toFixed(2)} (#${e.keyword_rank})` : "not matched"}</dd>
        </div>
        <div>
          <dt>Type</dt>
          <dd>{DOC_TYPE[m.document_type] || m.document_type}</dd>
        </div>
      </dl>

      <p className={`ev__text ${open ? "ev__text--open" : ""}`}>{e.text}</p>
      <div className="ev__actions">
        <button type="button" className="linkish" aria-expanded={open} onClick={() => setOpen((v) => !v)}>
          {open ? "Collapse passage" : "Read full passage"}
        </button>
        <span className="ev__file" title="Source file">
          {m.source_file}
        </span>
      </div>
      {m.locations?.length > 0 && (
        <ul className="tags" aria-label="Locations mentioned">
          {m.locations.slice(0, 5).map((l) => (
            <li key={l}>{l}</li>
          ))}
        </ul>
      )}
    </li>
  );
}

export default function EvidenceRail({ evidence, activeId, status }) {
  const [citedOnly, setCitedOnly] = useState(false);
  const anyCited = evidence.some((e) => e.cited);
  const shown = citedOnly ? evidence.filter((e) => e.cited) : evidence;
  const insufficient = status === "insufficient";

  return (
    <section className="rail" aria-labelledby="rail-title">
      <div className="rail__head">
        <h2 id="rail-title">Retrieved evidence</h2>
        {anyCited && (
          <label className="toggle">
            <input type="checkbox" checked={citedOnly} onChange={(ev) => setCitedOnly(ev.target.checked)} />
            Cited only
          </label>
        )}
      </div>
      <p className="rail__note">
        {insufficient
          ? "Closest passages found. None was relevant enough to answer from."
          : "Ranked by hybrid retrieval: vector similarity in Qdrant fused with BM25 keyword match."}
      </p>
      <ol className="ev-list">
        {shown.map((e) => (
          <EvidenceItem key={e.chunk_id} e={e} active={activeId === e.evidence_id} insufficient={insufficient} />
        ))}
      </ol>
    </section>
  );
}
