"use client";

import { ComponentDetailPanel } from "@/components/ComponentDetailPanel";
import { DiagramViewer } from "@/components/DiagramViewer";
import { Button } from "@/components/ui/button";
import type { JobPreviewResponse, JobStatusResponse } from "@/lib/types";
import { useCallback, useEffect, useMemo, useState } from "react";

const POLL_MS = 1200;

export default function GeneratePage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const base = `${apiUrl}/api/v1`;

  const [requirement, setRequirement] = useState("");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [preview, setPreview] = useState<JobPreviewResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const selections = useMemo(() => preview?.component_selections ?? {}, [preview]);
  const categories = useMemo(() => Object.keys(selections).sort(), [selections]);

  const fetchPreview = useCallback(
    async (id: string) => {
      const res = await fetch(`${base}/jobs/${id}/preview`);
      if (!res.ok) throw new Error(await res.text());
      const data = (await res.json()) as JobPreviewResponse;
      setPreview(data);
    },
    [base],
  );

  useEffect(() => {
    if (!jobId) return;
    let stop = false;

    const tick = async () => {
      try {
        const res = await fetch(`${base}/jobs/${jobId}/status`);
        if (!res.ok) return;
        const st = (await res.json()) as JobStatusResponse;
        if (stop) return;
        setStatus(st);
        if (st.status === "completed") {
          await fetchPreview(jobId);
        }
        if (st.status === "failed") {
          setError(st.error_message ?? "Generation failed");
        }
      } catch {
        /* ignore transient network errors while polling */
      }
    };

    void tick();
    const id = window.setInterval(tick, POLL_MS);
    return () => {
      stop = true;
      window.clearInterval(id);
    };
  }, [jobId, base, fetchPreview]);

  useEffect(() => {
    if (!selectedCategory && categories.length) {
      setSelectedCategory(categories[0] ?? null);
    }
  }, [categories, selectedCategory]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setPreview(null);
    setStatus(null);
    setJobId(null);
    setBusy(true);
    try {
      const res = await fetch(`${base}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ requirement }),
      });
      if (!res.ok) throw new Error(await res.text());
      const body = (await res.json()) as { job_id: string };
      setJobId(body.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  };

  const activeDecision = selectedCategory ? (selections[selectedCategory] ?? null) : null;

  return (
    <main className="mx-auto min-h-screen max-w-5xl px-4 py-10 md:px-8">
      <div className="mb-8 space-y-2">
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Phase 4 · Diagrams</p>
        <h1 className="font-serif text-3xl font-semibold tracking-tight">Generate & preview architecture</h1>
        <p className="max-w-2xl text-muted-foreground">
          Submit a design brief; when the job completes, inspect the overlaid SVG or a client-side Mermaid render, and
          open component trade-offs.
        </p>
      </div>

      <form onSubmit={onSubmit} className="mb-10 space-y-4">
        <label className="block text-sm font-medium">Requirement</label>
        <textarea
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          rows={6}
          placeholder="e.g. Design a RAG assistant for internal docs with PostgreSQL and Redis…"
          className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm shadow-sm outline-none ring-offset-background placeholder:text-muted-foreground focus-visible:ring-2 focus-visible:ring-ring"
          required
        />
        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={busy || !requirement.trim()}>
            {busy ? "Starting…" : "Generate"}
          </Button>
          {jobId ? (
            <span className="text-sm text-muted-foreground">
              Job <code className="rounded bg-muted px-1">{jobId}</code>
            </span>
          ) : null}
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {status ? (
          <p className="text-sm text-muted-foreground">
            Status: <span className="font-medium text-foreground">{status.status}</span>
            {status.progress != null ? ` · ${status.progress}%` : null}
            {status.current_step ? ` · ${status.current_step}` : null}
          </p>
        ) : null}
      </form>

      {preview?.status === "completed" ? (
        <div className="grid gap-8 lg:grid-cols-[1fr_280px]">
          <DiagramViewer mermaid={preview.mermaid} svg={preview.svg} title="Architecture" />

          <div className="space-y-3">
            <p className="text-sm font-medium">Components</p>
            <ul className="space-y-1">
              {categories.map((c) => (
                <li key={c}>
                  <button
                    type="button"
                    onClick={() => setSelectedCategory(c)}
                    className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition hover:bg-muted ${
                      selectedCategory === c ? "border-primary bg-muted/60" : "border-transparent"
                    }`}
                  >
                    <span className="font-medium capitalize">{c.replace(/_/g, " ")}</span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">
                      {selections[c]?.selected.name}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}

      <ComponentDetailPanel
        category={selectedCategory}
        decision={activeDecision}
        onClose={() => setSelectedCategory(null)}
      />
    </main>
  );
}
