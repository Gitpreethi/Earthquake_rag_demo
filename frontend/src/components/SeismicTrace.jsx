import React, { useEffect, useRef, useState } from "react";

// A seismogram-style trace. Quiet background noise while idle; while a
// question is being processed the trace runs and shows a burst, so the
// loading state is the signal itself.
function makePath(width, height, phase, active) {
  const mid = height / 2;
  const pts = [];
  const step = 3;
  for (let x = 0; x <= width; x += step) {
    const t = x / width;
    let y = Math.sin(x * 0.11 + phase) * 1.2 + Math.sin(x * 0.37 + phase * 1.7) * 0.8;
    if (active) {
      const centre = ((phase * 0.06) % 1.4) - 0.2; // burst travels across
      const d = (t - centre) * 9;
      const env = Math.exp(-d * d) * (height * 0.42);
      y += Math.sin(x * 0.9 + phase * 3) * env;
    }
    pts.push(`${x === 0 ? "M" : "L"}${x},${(mid + y).toFixed(1)}`);
  }
  return pts.join(" ");
}

export default function SeismicTrace({ active }) {
  const [phase, setPhase] = useState(0);
  const raf = useRef();
  const reduced = typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    if (!active || reduced) return undefined;
    const tick = () => {
      setPhase((p) => p + 0.35);
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [active, reduced]);

  return (
    <svg className={`trace ${active ? "trace--active" : ""}`} viewBox="0 0 1200 56" preserveAspectRatio="none" aria-hidden="true">
      <line x1="0" y1="28" x2="1200" y2="28" className="trace__axis" />
      <path d={makePath(1200, 56, phase, active)} className="trace__line" />
    </svg>
  );
}
