"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";

type Props = {
  mermaid?: string | null;
  svg?: string | null;
  title?: string;
};

export function DiagramViewer({ mermaid, svg, title = "Architecture diagram" }: Props) {
  const uid = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [tab, setTab] = useState<"svg" | "mermaid">("svg");
  const [mermaidError, setMermaidError] = useState<string | null>(null);

  const hasSvg = Boolean(svg && svg.trim());
  const hasMmd = Boolean(mermaid && mermaid.trim());

  useEffect(() => {
    if (!hasSvg && hasMmd) setTab("mermaid");
  }, [hasSvg, hasMmd]);

  useEffect(() => {
    if (tab !== "mermaid" || !hasMmd || !containerRef.current) return;

    let cancelled = false;
    setMermaidError(null);

    (async () => {
      try {
        const mermaidMod = await import("mermaid");
        const m = mermaidMod.default;
        m.initialize({
          startOnLoad: false,
          theme: "neutral",
          securityLevel: "strict",
        });
        const renderId = `mmd-${uid.replace(/:/g, "")}`;
        const { svg: rendered } = await m.render(renderId, (mermaid ?? "").trim());
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = rendered;
        }
      } catch (e) {
        if (!cancelled) {
          setMermaidError(e instanceof Error ? e.message : "Mermaid render failed");
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [tab, mermaid, hasMmd, uid]);

  const svgMarkup = useMemo(() => ({ __html: svg ?? "" }), [svg]);

  const effectiveTab = !hasSvg && hasMmd ? "mermaid" : tab;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-medium">{title}</p>
        <div className="flex rounded-lg border bg-muted/40 p-0.5 text-xs">
          <button
            type="button"
            disabled={!hasSvg}
            onClick={() => setTab("svg")}
            className={`rounded-md px-3 py-1 transition ${
              effectiveTab === "svg" ? "bg-background shadow-sm" : "text-muted-foreground"
            } ${!hasSvg ? "cursor-not-allowed opacity-50" : ""}`}
          >
            SVG preview
          </button>
          <button
            type="button"
            disabled={!hasMmd}
            onClick={() => setTab("mermaid")}
            className={`rounded-md px-3 py-1 transition ${
              effectiveTab === "mermaid" ? "bg-background shadow-sm" : "text-muted-foreground"
            } ${!hasMmd ? "cursor-not-allowed opacity-50" : ""}`}
          >
            Mermaid render
          </button>
        </div>
      </div>

      <div className="overflow-auto rounded-xl border bg-card">
        {effectiveTab === "svg" && hasSvg ? (
          <div
            className="diagram-svg-root min-h-[320px] p-4 [&_svg]:max-h-[560px] [&_svg]:w-full [&_svg]:object-contain"
            dangerouslySetInnerHTML={svgMarkup}
          />
        ) : null}

        {effectiveTab === "mermaid" && hasMmd ? (
          <div className="min-h-[320px] p-4">
            {mermaidError ? (
              <p className="text-sm text-destructive">{mermaidError}</p>
            ) : (
              <div ref={containerRef} className="flex justify-center [&_svg]:max-h-[560px] [&_svg]:w-full" />
            )}
          </div>
        ) : null}

        {!hasSvg && !hasMmd ? (
          <div className="flex min-h-[200px] items-center justify-center p-8 text-sm text-muted-foreground">
            No diagram payload yet.
          </div>
        ) : null}
      </div>

      {hasMmd && effectiveTab === "mermaid" ? (
        <details className="rounded-lg border bg-muted/30 p-3 text-sm">
          <summary className="cursor-pointer font-medium">Mermaid source</summary>
          <pre className="mt-2 max-h-48 overflow-auto whitespace-pre-wrap break-words font-mono text-xs text-muted-foreground">
            {mermaid}
          </pre>
        </details>
      ) : null}
    </div>
  );
}
