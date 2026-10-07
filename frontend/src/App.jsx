import React, { useCallback, useEffect, useRef, useState } from "react";
import { api } from "./api.js";
import SeismicTrace from "./components/SeismicTrace.jsx";
import AnswerBrief from "./components/AnswerBrief.jsx";
import EvidenceRail from "./components/EvidenceRail.jsx";

const FALLBACK_EXAMPLES = [
  "What information is available about the 2001 Gujarat earthquake?",
  "What does the Disaster Management Act 2005 say about disaster management?",
  "What earthquake information is available for Sikkim?",
  "Summarize the earthquake information available in the ISRO data.",
  "What emergency response information is present in the knowledge base?",
];

const DOC_TYPE = {
  legislation: "Legislation",
  standard_operating_procedure: "Operating procedure",
  report: "Report",
  seismic_catalog: "Seismic catalogue",
};

function Corpus({ corpus }) {
  if (!corpus) return null;
  return (
    <section className="corpus" aria-labelledby="corpus-title">
      <h2 id="corpus-title">Indexed documents</h2>
      <ul>
        {corpus.documents.map((d) => (
          <li key={d.source_file}>
            <span className="corpus__name">{d.document_name}</span>
            <span className="corpus__meta">
              {DOC_TYPE[d.document_type] || d.document_type}, {d.pages ? `${d.pages} pages` : `sheet ${d.sheets?.join(", ")}`},{" "}
              {d.chunks} passages
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function Loading({ question }) {
  return (
    <div className="loading" role="status">
      <p className="loading__q">“{question}”</p>
      <ol className="loading__steps">
        <li>Searching vector index and keyword index</li>
        <li>Fusing and ranking evidence</li>
        <li>Writing an answer from the evidence only</li>
      </ol>
    </div>
  );
}

export default function App() {
  const [health, setHealth] = useState(null);
  const [corpus, setCorpus] = useState(null);
  const [examples, setExamples] = useState(FALLBACK_EXAMPLES);
  const [question, setQuestion] = useState("");
  const [asked, setAsked] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const inputRef = useRef(null);

  useEffect(() => {
    api.health().then(setHealth).catch((e) => setError(e.message));
    api.corpus().then(setCorpus).catch(() => {});
    api.examples().then((r) => r.examples?.length && setExamples(r.examples)).catch(() => {});
  }, []);

  const ask = useCallback(
    async (q) => {
      const text = (q ?? question).trim();
      if (text.length < 3 || loading) return;
      setQuestion(text);
      setAsked(text);
      setLoading(true);
      setError(null);
      setResult(null);
      setActiveId(null);
      try {
        setResult(await api.ask(text));
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    },
    [question, loading]
  );

  const onCite = (id) => {
    setActiveId(null);
    requestAnimationFrame(() => setActiveId(id));
  };

  const llm = health?.llm;
  const empty = health && health.chunks_indexed === 0;

  return (
    <div className="app">
      <header className="masthead">
        <div className="masthead__row">
          <div>
            <h1>India Earthquake Knowledge Desk</h1>
            <p className="masthead__sub">Answers drawn only from the indexed documents, with every source shown.</p>
          </div>
          {health && (
            <dl className="sys">
              <div>
                <dt>Passages indexed</dt>
                <dd>{health.chunks_indexed.toLocaleString("en-IN")}</dd>
              </div>
              <div>
                <dt>Documents</dt>
                <dd>{corpus ? corpus.documents.length : "–"}</dd>
              </div>
              <div>
                <dt>Answer engine</dt>
                <dd>{llm?.generative ? llm.model : "Extractive (no LLM)"}</dd>
              </div>
            </dl>
          )}
        </div>
        <SeismicTrace active={loading} />
      </header>

      <main className="main">
        <form
          className="ask"
          onSubmit={(e) => {
            e.preventDefault();
            ask();
          }}
        >
          <label htmlFor="q" className="ask__label">
            Ask about earthquakes, response procedures or disaster policy in India
          </label>
          <div className="ask__row">
            <textarea
              id="q"
              ref={inputRef}
              rows={2}
              value={question}
              placeholder="e.g. What does the NDRF procedure say about search and rescue after an earthquake?"
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  ask();
                }
              }}
            />
            <button type="submit" className="ask__btn" disabled={loading || question.trim().length < 3}>
              {loading ? "Searching…" : "Ask"}
            </button>
          </div>
          <div className="examples" aria-label="Example questions">
            {examples.map((ex) => (
              <button key={ex} type="button" className="example" disabled={loading} onClick={() => ask(ex)}>
                {ex}
              </button>
            ))}
          </div>
        </form>

        {empty && (
          <div className="notice notice--warn">
            The knowledge base is empty. Add PDF or Excel files to <code>data/</code> and run{" "}
            <code>python -m scripts.ingest</code> from <code>backend/</code>.
          </div>
        )}
        {error && (
          <div className="notice notice--error" role="alert">
            <strong>Request failed.</strong> {error}
          </div>
        )}

        {loading && <Loading question={asked} />}

        {result && !loading && (
          <div className="results">
            <div className="results__answer">
              <p className="asked">“{result.question}”</p>
              <AnswerBrief result={result} onCite={onCite} />
            </div>
            <EvidenceRail evidence={result.evidence} activeId={activeId} status={result.status} />
          </div>
        )}

        {!result && !loading && !error && (
          <div className="intro">
            <section className="howto">
              <h2>How answers are produced</h2>
              <ol>
                <li>Your question is searched two ways: by meaning (vector index in Qdrant) and by exact terms (BM25).</li>
                <li>The two rankings are fused and the top passages become the only evidence.</li>
                <li>The language model writes an answer from that evidence, citing passages as E1, E2…</li>
                <li>If the evidence does not support an answer, the desk says so instead of guessing.</li>
              </ol>
            </section>
            <Corpus corpus={corpus} />
          </div>
        )}
      </main>
      <footer className="foot">
        <p>
          Prototype for research use. Answers can only be as complete as the indexed documents; always verify against
          the cited source before operational use.
        </p>
      </footer>
    </div>
  );
}
