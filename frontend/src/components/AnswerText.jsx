import React from "react";

// Minimal, safe markdown renderer for answers: paragraphs, bullet lists,
// **bold**, and [E#] citations rendered as buttons that jump to evidence.
function renderInline(text, onCite, keyBase) {
  const parts = text.split(/(\[E\d+\]|\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map((p, i) => {
    const key = `${keyBase}-${i}`;
    const cite = p.match(/^\[(E\d+)\]$/);
    if (cite) {
      return (
        <button key={key} type="button" className="cite" onClick={() => onCite(cite[1])} title={`Show evidence ${cite[1]}`}>
          {cite[1]}
        </button>
      );
    }
    const bold = p.match(/^\*\*([^*]+)\*\*$/);
    if (bold) return <strong key={key}>{bold[1]}</strong>;
    return <React.Fragment key={key}>{p}</React.Fragment>;
  });
}

export default function AnswerText({ text, onCite }) {
  const blocks = [];
  let list = null;
  text.split("\n").forEach((raw, i) => {
    const line = raw.trimEnd();
    const bullet = line.match(/^\s*(?:[-*•]|\d+\.)\s+(.*)$/);
    if (bullet) {
      if (!list) {
        list = [];
        blocks.push({ type: "ul", items: list, key: `ul-${i}` });
      }
      list.push({ text: bullet[1], key: `li-${i}` });
      return;
    }
    list = null;
    if (!line.trim()) return;
    const heading = line.match(/^#{1,4}\s+(.*)$/);
    if (heading) blocks.push({ type: "h", text: heading[1], key: `h-${i}` });
    else blocks.push({ type: "p", text: line, key: `p-${i}`, warn: line.startsWith("⚠") });
  });

  return (
    <div className="answer-text">
      {blocks.map((b) => {
        if (b.type === "ul")
          return (
            <ul key={b.key}>
              {b.items.map((it) => (
                <li key={it.key}>{renderInline(it.text, onCite, it.key)}</li>
              ))}
            </ul>
          );
        if (b.type === "h") return <h4 key={b.key}>{renderInline(b.text, onCite, b.key)}</h4>;
        return (
          <p key={b.key} className={b.warn ? "answer-warn" : undefined}>
            {renderInline(b.text, onCite, b.key)}
          </p>
        );
      })}
    </div>
  );
}
