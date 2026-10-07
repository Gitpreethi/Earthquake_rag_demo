// Thin client for the FastAPI backend. In dev, Vite proxies /api to :8000;
// in production the backend serves this bundle, so relative URLs work.
const BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the RAG service. Check that the backend is running on port 8000.");
  }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body.detail || `The service returned ${res.status}.`);
  }
  return body;
}

export const api = {
  health: () => request("/api/health"),
  corpus: () => request("/api/corpus"),
  examples: () => request("/api/examples"),
  ask: (question, topK) =>
    request("/api/ask", { method: "POST", body: JSON.stringify({ question, top_k: topK || undefined }) }),
};
