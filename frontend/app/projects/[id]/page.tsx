"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, ChevronRight, Layers, Clock, AlertCircle, Download } from "lucide-react";
import { DiagramViewer } from "@/components/DiagramViewer";
import { ComponentDetailPanel } from "@/components/ComponentDetailPanel";
import { DocumentPreviewGrid } from "@/components/DocumentPreviewCard";
import { DownloadPanel } from "@/components/DownloadPanel";
import type { ComponentDecision } from "@/lib/types";

type ProjectDetail = {
  id: string;
  name: string;
  description?: string | null;
  domain?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  requirements?: Record<string, unknown> | null;
  component_selections?: Record<string, ComponentDecision> | null;
  generated_files?: Record<string, string> | null;
};

type JobPreview = {
  status: string;
  mermaid?: string | null;
  svg?: string | null;
  component_selections: Record<string, ComponentDecision>;
};

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "long", timeStyle: "short" }).format(
    new Date(iso),
  );
}

export default function ProjectDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const { id } = params;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const base = `${apiUrl}/api/v1`;

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [preview, setPreview] = useState<JobPreview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "diagram" | "documents">("overview");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${base}/projects/${id}`);
        if (!res.ok) throw new Error(`Project not found (${res.status})`);
        const data = (await res.json()) as ProjectDetail;
        setProject(data);

        if (data.component_selections) {
          setPreview({
            status: data.status,
            mermaid: null,
            svg: null,
            component_selections: data.component_selections,
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load project");
      } finally {
        setLoading(false);
      }
    };

    void fetchData();
  }, [id, base]);

  const selections = preview?.component_selections ?? {};
  const categories = Object.keys(selections).sort();
  const activeDecision = selectedCategory ? (selections[selectedCategory] ?? null) : null;

  if (loading) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="space-y-6 animate-pulse">
          <div className="skeleton h-4 w-32 rounded" />
          <div className="skeleton h-8 w-64 rounded" />
          <div className="skeleton h-4 w-96 rounded" />
          <div className="grid gap-4 sm:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="skeleton h-24 rounded-xl" />
            ))}
          </div>
        </div>
      </main>
    );
  }

  if (error || !project) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <Link
          href="/projects"
          className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden />
          Back to Projects
        </Link>
        <div className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-4 mt-4" role="alert">
          <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" aria-hidden />
          <div>
            <p className="text-sm font-medium text-destructive">{error ?? "Project not found"}</p>
            <p className="text-xs text-muted-foreground mt-1">
              The project may have been deleted or the ID is invalid.
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-dvh max-w-6xl px-4 py-10 sm:px-6">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-xs text-muted-foreground animate-fade-in">
        <Link href="/" className="hover:text-foreground transition">ArchDLoom</Link>
        <ChevronRight className="h-3 w-3" aria-hidden />
        <Link href="/projects" className="hover:text-foreground transition">Projects</Link>
        <ChevronRight className="h-3 w-3" aria-hidden />
        <span className="text-foreground truncate max-w-[200px]">{project.name}</span>
      </nav>

      {/* Project header */}
      <div className="mb-6 animate-slide-up">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-green-500/10 border border-green-500/20">
              <Layers className="h-5 w-5 text-green-400" aria-hidden />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight sm:text-2xl">{project.name}</h1>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                {project.domain && (
                  <span className="rounded-full border border-border/60 bg-muted px-2 py-0.5 capitalize">
                    {project.domain}
                  </span>
                )}
                <span
                  className={`rounded-full border px-2 py-0.5 capitalize font-medium ${
                    project.status === "completed"
                      ? "border-green-500/20 bg-green-500/10 text-green-400"
                      : "border-border/60 text-muted-foreground bg-muted"
                  }`}
                >
                  {project.status}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" aria-hidden />
                  <time dateTime={project.updated_at}>{formatDate(project.updated_at)}</time>
                </span>
              </div>
            </div>
          </div>

          {project.status === "completed" && (
            <Link
              href={`/generate`}
              className="inline-flex items-center gap-2 rounded-lg border border-border/60 bg-card px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <Download className="h-4 w-4" aria-hidden />
              New Design
            </Link>
          )}
        </div>

        {project.description && (
          <p className="mt-3 max-w-2xl text-sm text-muted-foreground leading-relaxed">
            {project.description}
          </p>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-xl border border-border/60 bg-muted/20 p-1 w-fit" role="tablist">
        {(["overview", "diagram", "documents"] as const).map((tab) => (
          <button
            key={tab}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            onClick={() => setActiveTab(tab)}
            className={`rounded-lg px-4 py-1.5 text-sm font-medium capitalize transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
              activeTab === tab
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
        {/* Tab content */}
        <div>
          {activeTab === "overview" && (
            <div className="space-y-5 animate-fade-in">
              {/* Component selections overview */}
              {categories.length > 0 ? (
                <div className="space-y-3">
                  <p className="text-sm font-semibold text-foreground">Component Selections</p>
                  <ul className="grid gap-3 sm:grid-cols-2" role="list">
                    {categories.map((cat) => {
                      const decision = selections[cat];
                      return (
                        <li key={cat}>
                          <button
                            type="button"
                            onClick={() => setSelectedCategory(cat)}
                            className={`w-full rounded-xl border p-4 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                              selectedCategory === cat
                                ? "border-green-500/40 bg-green-500/10"
                                : "border-border/60 bg-card hover:border-border hover:bg-muted/40"
                            }`}
                            aria-pressed={selectedCategory === cat}
                          >
                            <p className="text-xs font-medium text-muted-foreground capitalize mb-1">
                              {cat.replace(/_/g, " ")}
                            </p>
                            <p className="text-sm font-semibold text-foreground truncate">
                              {decision?.selected.name}
                            </p>
                            {decision?.selected.vendor && (
                              <p className="text-xs text-muted-foreground">{decision.selected.vendor}</p>
                            )}
                            {decision?.estimated_monthly_cost_usd != null && (
                              <p className="mt-2 text-xs tabular-nums text-green-400 font-medium">
                                ${decision.estimated_monthly_cost_usd.toLocaleString()}/mo
                              </p>
                            )}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : (
                <div className="rounded-xl border border-dashed border-border p-8 text-center">
                  <p className="text-sm text-muted-foreground">No component data available for this project.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "diagram" && (
            <div className="animate-fade-in">
              {preview?.mermaid || preview?.svg ? (
                <DiagramViewer
                  mermaid={preview.mermaid}
                  svg={preview.svg}
                  title={`${project.name} — Architecture`}
                />
              ) : (
                <div className="rounded-xl border border-dashed border-border py-16 text-center">
                  <p className="text-sm text-muted-foreground">
                    No diagram available for this project.
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === "documents" && (
            <div className="animate-fade-in">
              <DocumentPreviewGrid systemName={project.name} />
            </div>
          )}
        </div>

        {/* Sidebar */}
        <aside className="space-y-4">
          {project.status === "completed" && (
            <DownloadPanel jobId={project.id} apiBase={`${apiUrl}/api/v1`} />
          )}

          <div className="rounded-xl border border-border/60 bg-card p-5 space-y-3">
            <p className="text-sm font-semibold text-foreground">Project Info</p>
            <dl className="space-y-2 text-xs">
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Project ID</dt>
                <dd>
                  <code className="font-mono rounded bg-muted px-1">{project.id.slice(0, 12)}…</code>
                </dd>
              </div>
              {project.domain && (
                <div className="flex justify-between gap-2">
                  <dt className="text-muted-foreground">Domain</dt>
                  <dd className="capitalize text-foreground">{project.domain}</dd>
                </div>
              )}
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Created</dt>
                <dd className="text-foreground text-right">{formatDate(project.created_at)}</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Updated</dt>
                <dd className="text-foreground text-right">{formatDate(project.updated_at)}</dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt className="text-muted-foreground">Components</dt>
                <dd className="text-foreground">{categories.length}</dd>
              </div>
            </dl>
          </div>

          <Link
            href="/projects"
            className="flex items-center gap-2 rounded-lg border border-border/60 px-4 py-2.5 text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <ArrowLeft className="h-4 w-4" aria-hidden />
            All Projects
          </Link>
        </aside>
      </div>

      <ComponentDetailPanel
        category={selectedCategory}
        decision={activeDecision}
        onClose={() => setSelectedCategory(null)}
      />
    </main>
  );
}
