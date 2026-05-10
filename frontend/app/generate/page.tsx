"use client";

import { ComponentDetailPanel } from "@/components/ComponentDetailPanel";
import { DiagramViewer } from "@/components/DiagramViewer";
import { DocumentPreviewGrid } from "@/components/DocumentPreviewCard";
import type { DocType } from "@/components/DocumentPreviewCard";
import { DownloadPanel } from "@/components/DownloadPanel";
import { GenerationProgress } from "@/components/GenerationProgress";
import { Button } from "@/components/ui/button";
import type { JobPreviewResponse, JobStatusResponse } from "@/lib/types";
import { Sparkles, ChevronRight } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

const POLL_MS = 1200;

const DOC_ITEMS: { key: DocType; abbr: string; desc: string }[] = [
  { key: "prd",          abbr: "PRD", desc: "Business requirements & user stories" },
  { key: "hld",          abbr: "HLD", desc: "System architecture & component rationale" },
  { key: "lld",          abbr: "LLD", desc: "Schema design & service internals" },
  { key: "evolution",    abbr: "Evo", desc: "MVP → Growth → Enterprise roadmap" },
  { key: "architecture", abbr: "Dia", desc: "Architecture with real vendor icons" },
];

const ALL_DOCS = new Set<DocType>(DOC_ITEMS.map((d) => d.key));

const EXAMPLE_PROMPTS = [
  "Design a RAG-based internal knowledge assistant for a 500-person company using PostgreSQL and AWS infrastructure, targeting 99.9% uptime.",
  "Build a real-time fraud detection system for a fintech startup processing 10,000 transactions per second with GDPR compliance.",
  "Create a multi-tenant SaaS platform for healthcare data analytics with HIPAA compliance and 1M monthly active users.",
];

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
  const [panelOpen, setPanelOpen] = useState(false);
  const [selectedDocs, setSelectedDocs] = useState<Set<DocType>>(new Set(ALL_DOCS));

  const toggleDoc = (key: DocType) => {
    setSelectedDocs((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size === 1) return prev; // keep at least one
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

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
        if (st.status === "completed") await fetchPreview(jobId);
        if (st.status === "failed") setError(st.error_message ?? "Generation failed");
      } catch {
        /* ignore transient network errors */
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
  }, [categories]); // intentionally omit selectedCategory — only auto-select when categories first arrive

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
        body: JSON.stringify({ requirement, selected_documents: Array.from(selectedDocs) }),
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
  const isCompleted = preview?.status === "completed";
  const isInProgress = Boolean(jobId) && !isCompleted && status?.status !== "failed";

  return (
    <main className="mx-auto min-h-dvh max-w-6xl px-4 py-10 sm:px-6">
      {/* Header */}
      <div className="mb-8 space-y-2 animate-fade-in">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>ArchDLoom</span>
          <ChevronRight className="h-3 w-3" aria-hidden />
          <span className="text-foreground">Generate</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          Generate System Design
        </h1>
        <p className="max-w-2xl text-sm text-muted-foreground">
          Describe your system requirements in natural language. Claude AI will parse, select
          components, and generate PRD, HLD, LLD, and architecture diagrams.
        </p>
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        {/* Main column */}
        <div className="space-y-6">
          {/* Input form */}
          <form onSubmit={onSubmit} className="rounded-xl border border-border/60 bg-card p-6 space-y-4">
            <label htmlFor="requirement" className="block text-sm font-medium text-foreground">
              System Requirement{" "}
              <span className="text-muted-foreground font-normal">(required)</span>
            </label>
            <textarea
              id="requirement"
              value={requirement}
              onChange={(e) => setRequirement(e.target.value)}
              rows={6}
              placeholder="e.g. Design a RAG assistant for internal docs with 100K users, PostgreSQL + Redis, deployed on AWS, targeting 99.9% uptime and GDPR compliance…"
              className="w-full resize-none rounded-lg border border-input bg-muted/30 px-3 py-2.5 text-sm text-foreground shadow-sm outline-none ring-offset-background placeholder:text-muted-foreground/60 focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring transition"
              aria-describedby="req-helper"
              required
            />
            <p id="req-helper" className="text-xs text-muted-foreground">
              Include scale (users, requests/sec), domain, tech preferences, and compliance needs for best results.
            </p>

            {/* Example prompts */}
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">Try an example:</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_PROMPTS.map((prompt, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setRequirement(prompt)}
                    className="rounded-md border border-border/60 bg-muted/30 px-2.5 py-1 text-xs text-muted-foreground transition hover:border-border hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    {["RAG Assistant", "Fraud Detection", "Healthcare SaaS"][i]}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Button
                type="submit"
                disabled={busy || !requirement.trim() || isInProgress}
                aria-busy={busy}
                className="bg-green-500 text-slate-950 hover:bg-green-400 font-semibold glow-green-sm disabled:opacity-50"
              >
                <Sparkles className="mr-2 h-4 w-4" aria-hidden />
                {busy ? "Starting…" : isInProgress ? "Generating…" : "Generate Design"}
              </Button>
              {jobId && (
                <p className="text-xs text-muted-foreground">
                  Job{" "}
                  <code className="rounded bg-muted px-1 font-mono">{jobId.slice(0, 8)}</code>
                </p>
              )}
            </div>

            {error && (
              <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2" role="alert">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
          </form>

          {/* Progress */}
          {status && !isCompleted && (
            <div className="animate-fade-in">
              <GenerationProgress status={status} />
            </div>
          )}

          {/* Diagram viewer */}
          {isCompleted && preview && (
            <div className="animate-fade-in space-y-6">
              <DiagramViewer mermaid={preview.mermaid} svg={preview.svg} title="Architecture Diagram" />

              {/* Component selector */}
              <div className="space-y-3">
                <p className="text-sm font-medium text-foreground">Component Selections</p>
                <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3" role="list">
                  {categories.map((c) => (
                    <li key={c}>
                      <button
                        type="button"
                        onClick={() => { setSelectedCategory(c); setPanelOpen(true); }}
                        className={`w-full rounded-lg border px-3 py-2.5 text-left text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                          panelOpen && selectedCategory === c
                            ? "border-green-500/40 bg-green-500/10 text-foreground"
                            : "border-border/60 bg-card hover:border-border hover:bg-muted/40 text-muted-foreground hover:text-foreground"
                        }`}
                        aria-pressed={panelOpen && selectedCategory === c}
                      >
                        <span className="block font-medium capitalize text-foreground">
                          {c.replace(/_/g, " ")}
                        </span>
                        <span className="block text-xs text-muted-foreground mt-0.5 truncate">
                          {selections[c]?.selected?.name}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Document previews */}
              <DocumentPreviewGrid selectedTypes={selectedDocs} />
            </div>
          )}
        </div>

        {/* Sidebar */}
        <aside className="space-y-5">
          {/* Generation guide */}
          {!jobId && (
            <div className="rounded-xl border border-border/60 bg-card p-5 space-y-4">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-semibold text-foreground">What gets generated</p>
                <span className="text-xs text-muted-foreground tabular-nums">
                  {selectedDocs.size}/{DOC_ITEMS.length} selected
                </span>
              </div>

              <ul className="space-y-1.5" role="list">
                {DOC_ITEMS.map((item) => {
                  const checked = selectedDocs.has(item.key);
                  return (
                    <li key={item.key}>
                      <label className="flex cursor-pointer items-start gap-2.5 rounded-lg p-1.5 transition hover:bg-muted/40 group">
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleDoc(item.key)}
                          className="mt-0.5 h-3.5 w-3.5 shrink-0 cursor-pointer accent-green-500 rounded"
                          aria-label={`Include ${item.abbr} in generation`}
                        />
                        <span
                          className={`mt-0.5 inline-flex h-5 w-8 shrink-0 items-center justify-center rounded font-mono text-xs font-medium transition ${
                            checked
                              ? "bg-green-500/15 text-green-400"
                              : "bg-muted text-muted-foreground/50"
                          }`}
                        >
                          {item.abbr}
                        </span>
                        <span
                          className={`text-xs leading-snug transition ${
                            checked
                              ? "text-muted-foreground group-hover:text-foreground"
                              : "text-muted-foreground/40 line-through"
                          }`}
                        >
                          {item.desc}
                        </span>
                      </label>
                    </li>
                  );
                })}
              </ul>

              <p className="text-xs text-muted-foreground border-t border-border/60 pt-3">
                Average generation time:{" "}
                <span className="text-foreground font-medium">2–3 minutes</span>
              </p>
            </div>
          )}

          {/* Download panel when complete */}
          {isCompleted && jobId && (
            <div className="animate-fade-in">
              <DownloadPanel jobId={jobId} apiBase={base} selectedDocs={selectedDocs} />
            </div>
          )}

          {/* In-progress status sidebar */}
          {isInProgress && status && (
            <div className="rounded-xl border border-border/60 bg-card p-5 animate-fade-in">
              <p className="text-sm font-semibold text-foreground mb-3">Generation status</p>
              <div className="space-y-2 text-xs text-muted-foreground">
                <div className="flex justify-between">
                  <span>Status</span>
                  <span className="text-foreground font-medium capitalize">{status.status}</span>
                </div>
                {status.progress != null && (
                  <div className="flex justify-between">
                    <span>Progress</span>
                    <span className="text-green-400 tabular-nums font-medium">{status.progress}%</span>
                  </div>
                )}
                {status.current_step && (
                  <div className="pt-1 border-t border-border/40">
                    <p className="text-foreground">{status.current_step}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </aside>
      </div>

      <ComponentDetailPanel
        category={panelOpen ? selectedCategory : null}
        decision={panelOpen ? activeDecision : null}
        onClose={() => setPanelOpen(false)}
      />
    </main>
  );
}
