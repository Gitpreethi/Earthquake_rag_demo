"""Unit tests for pipeline components that do not need the index or an LLM.

Run from backend/:  python -m pytest -q
"""
from app.generation.rag import _parse_llm_json, _validate_citations
from app.index.keyword import tokenize
from app.ingestion.chunking import detect_heading, parse_magnitude, parse_place
from app.ingestion.cleaning import clean_lines, lines_to_paragraphs
from app.ingestion.enrichment import tag_locations
from app.retrieval.hybrid import diversify, rrf_fuse
from app.retrieval.query import build_query


def test_clean_lines_removes_noise():
    text = "12\n. . .\n,,\nThe Act extends to the whole of India.\nRunning Header Text\ndisas-\nter management"
    lines = clean_lines(text, repeated={"running header text"})
    assert lines == ["The Act extends to the whole of India.", "disaster management"]


def test_paragraph_merging_keeps_list_items():
    paras = lines_to_paragraphs(["The authority shall", "prepare a plan.", "(a) provide shelter;", "(b) provide food."])
    assert paras[0] == "The authority shall prepare a plan."
    assert len(paras) == 3


def test_heading_detection():
    assert detect_heading("CHAPTER III", "STATE DISASTER MANAGEMENT AUTHORITY")[0] == 0
    lvl, title = detect_heading("44. National Disaster Response Force.—(1) There shall be constituted")
    assert lvl == 1 and title.startswith("Section 44.")
    assert detect_heading("9. ADMINISTRATION AND LOGISTIC ARRANGEMENTS:")[0] == 1
    assert detect_heading("the district authority shall act as the planning body.") is None


def test_catalogue_parsing():
    assert parse_magnitude("4.7[Mb]") == (4.7, "Mb")
    assert parse_place("26km NW of Uttarkashi, Uttarakhand, India") == ("Uttarakhand", "India")
    assert parse_place("125km WNW of Kathmandu, Nepal") == ("Nepal", "Nepal")
    assert parse_place("236km NNE of Leh, Laddakh, India") == ("Ladakh", "India")


def test_location_tags():
    assert "Gujarat" in tag_locations("Lessons from the Bhuj earthquake in Kutch")
    assert tag_locations("No place here") == []


def test_query_building_strips_filler_and_expands_acronyms():
    q = build_query("What information is available about NDRF in the ISRO data?")
    assert "inform" not in q.keyword_tokens and "data" not in q.keyword_tokens
    assert "national" in q.keyword_tokens and "isro" in q.entity_terms


def test_rrf_fusion_and_diversity():
    p = lambda src, sec=None: {"source_file": src, "section": sec}  # noqa: E731
    dense = [("a", 0.9, p("x")), ("b", 0.8, p("y"))]
    kw = [("b", 12.0, p("y")), ("c", 5.0, p("z"))]
    fused = rrf_fuse(dense, kw, k=60)
    assert fused[0]["id"] == "b"                 # found by both methods
    recs = [{"id": str(i), "payload": p("x", "s"), "fused": 1 - i / 10} for i in range(5)] + [{"id": "z", "payload": p("y"), "fused": 0.1}]
    out = diversify(recs, top_k=3, max_per_source=4, max_per_section=2)
    assert [r["id"] for r in out] == ["0", "1", "z"]


def test_citation_validation_and_json_parsing():
    parsed = _parse_llm_json('```json\n{"status":"partial","answer":"A [E1] B [E9].","used_evidence":["E1"]}\n```')
    assert parsed["status"] == "partial"
    ans, cited, invalid = _validate_citations(parsed["answer"], {"E1", "E2"})
    assert cited == ["E1"] and invalid == ["E9"] and "[E9]" not in ans


def test_tokenizer_stems_consistently():
    assert tokenize("Earthquakes recorded") == tokenize("earthquake records")
