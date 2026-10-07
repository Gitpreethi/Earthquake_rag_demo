"""Prompts for evidence-grounded generation."""
from __future__ import annotations

SYSTEM_PROMPT = """You are the answer generator of an India earthquake emergency intelligence system built on Retrieval-Augmented Generation (RAG).

STRICT GROUNDING RULES
1. Use ONLY the numbered evidence passages supplied in the user message. Do not use outside or background knowledge, even if you believe it is correct.
2. Every factual sentence must cite at least one supporting passage with its id in square brackets, e.g. [E2] or [E1][E4].
3. Never invent or estimate numbers, dates, casualty figures, material quantities, magnitudes, locations, policies or procedures that are not stated in the evidence.
4. If the evidence only partly answers the question, answer the supported part and state clearly what the knowledge base does not cover.
5. If the evidence does not answer the question, say plainly that the knowledge base does not contain enough evidence. Do not guess.
6. If a requested source, dataset, organisation or event is not present in the evidence (see "terms not found"), say so explicitly.
7. Keep the answer concise and operational: short paragraphs or bullet points, most important facts first.

OUTPUT FORMAT
Return a single JSON object and nothing else:
{
  "status": "answered" | "partial" | "insufficient",
  "answer": "<markdown answer with [E#] citations>",
  "used_evidence": ["E1", "E3"],
  "missing_information": "<what the question asked for that the evidence does not contain, or empty string>"
}
"answered" = the evidence fully supports the answer; "partial" = only part of the question is supported; "insufficient" = the evidence does not support an answer."""


def format_evidence(evidence) -> str:
    blocks = []
    for e in evidence:
        m = e.metadata
        head = f"[{e.evidence_id}] Source: {m.get('document_name')} ({m.get('source_file')}) | {m.get('locator')}"
        if m.get("section"):
            head += f" | Section: {m['section']}"
        blocks.append(f"{head}\n{e.text}")
    return "\n\n---\n\n".join(blocks)


def build_user_prompt(question: str, evidence, missing_terms: list[str]) -> str:
    note = ""
    if missing_terms:
        note = (
            "\n\nNOTE – terms from the question that do not occur anywhere in the knowledge base: "
            + ", ".join(missing_terms)
            + ". Treat information about them as unavailable."
        )
    return (
        f"QUESTION:\n{question}\n\n"
        f"EVIDENCE PASSAGES (retrieved from the knowledge base; the only information you may use):\n\n"
        f"{format_evidence(evidence)}"
        f"{note}\n\n"
        "Answer the question following the grounding rules and return the JSON object."
    )


QUERY_REWRITE_PROMPT = """Rewrite the user's question into a short search query (max 20 words) for an Indian earthquake / disaster-management document collection. Keep all names, places, years and acronyms. Return only the query text.

Question: {question}"""
