"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Layers, Plus, Search, Folder, Clock, ChevronRight, Trash2, AlertCircle } from "lucide-react";

type Project = {
  id: string;
  name: string;
  description?: string | null;
  domain?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
};

const DOMAIN_COLORS: Record<string, string> = {
  "e-commerce": "text-blue-400 bg-blue-400/10 border-blue-400/20",
  healthcare: "text-green-400 bg-green-400/10 border-green-400/20",
  fintech: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
  ai: "text-purple-400 bg-purple-400/10 border-purple-400/20",
  saas: "text-cyan-400 bg-cyan-400/10 border-cyan-400/20",
};

function domainBadge(domain?: string | null) {
  if (!domain) return "text-muted-foreground bg-muted border-border/60";
  const key = Object.keys(DOMAIN_COLORS).find((k) => domain.toLowerCase().includes(k));
  return key ? DOMAIN_COLORS[key] : "text-muted-foreground bg-muted border-border/60";
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(iso),
  );
}

export default function ProjectsPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const base = `${apiUrl}/api/v1`;

  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const fetchProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${base}/projects`);
      if (!res.ok) throw new Error(`Failed to load projects (${res.status})`);
      const data = (await res.json()) as Project[];
      setProjects(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchProjects();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      const res = await fetch(`${base}/projects/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch {
      /* keep in list if delete fails */
    } finally {
      setDeletingId(null);
      setConfirmDeleteId(null);
    }
  };

  const filtered = projects.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      (p.description ?? "").toLowerCase().includes(search.toLowerCase()) ||
      (p.domain ?? "").toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <main className="mx-auto min-h-dvh max-w-6xl px-4 py-10 sm:px-6">
      {/* Header */}
      <div className="mb-8 flex flex-wrap items-start justify-between gap-4 animate-fade-in">
        <div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
            <span>ArchDLoom</span>
            <ChevronRight className="h-3 w-3" aria-hidden />
            <span className="text-foreground">Projects</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">My Projects</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Saved architecture designs and generated documentation.
          </p>
        </div>
        <Link
          href="/generate"
          className="inline-flex items-center gap-2 rounded-lg bg-green-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-green-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring glow-green-sm"
        >
          <Plus className="h-4 w-4" aria-hidden />
          New Design
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" aria-hidden />
        <input
          type="search"
          placeholder="Search projects by name, domain, or description…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search projects"
          className="w-full rounded-lg border border-input bg-muted/30 py-2.5 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring transition"
        />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3" role="alert">
          <AlertCircle className="h-4 w-4 shrink-0 text-destructive mt-0.5" aria-hidden />
          <div>
            <p className="text-sm text-destructive font-medium">Failed to load projects</p>
            <p className="text-xs text-muted-foreground mt-0.5">{error}</p>
          </div>
          <button
            onClick={fetchProjects}
            className="ml-auto rounded-md px-3 py-1 text-xs border border-border text-foreground hover:bg-muted transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-label="Loading projects" role="list">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <li key={i} className="rounded-xl border border-border/60 bg-card p-5 space-y-3">
              <div className="skeleton h-4 w-32 rounded" />
              <div className="skeleton h-3 w-48 rounded" />
              <div className="skeleton h-3 w-20 rounded" />
              <div className="flex gap-2 pt-1">
                <div className="skeleton h-5 w-16 rounded-full" />
                <div className="skeleton h-5 w-20 rounded-full" />
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Projects grid */}
      {!loading && !error && (
        <>
          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20 text-center">
              <Folder className="h-12 w-12 text-muted-foreground/40 mb-4" aria-hidden />
              <p className="text-sm font-medium text-muted-foreground">
                {search ? "No projects match your search" : "No projects yet"}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                {search ? "Try different keywords" : "Generate your first system design to get started"}
              </p>
              {!search && (
                <Link
                  href="/generate"
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-green-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-green-400"
                >
                  <Plus className="h-4 w-4" aria-hidden />
                  Generate Design
                </Link>
              )}
            </div>
          ) : (
            <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" role="list">
              {filtered.map((project) => (
                <li key={project.id} className="group relative">
                  <Link
                    href={`/projects/${project.id}`}
                    className="card-hover block rounded-xl border border-border/60 bg-card p-5 space-y-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <Layers className="h-4 w-4 shrink-0 text-green-400" aria-hidden />
                        <h2 className="truncate text-sm font-semibold text-foreground">{project.name}</h2>
                      </div>
                      <span
                        className={`shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium capitalize ${
                          project.status === "completed"
                            ? "border-green-500/20 bg-green-500/10 text-green-400"
                            : project.status === "failed"
                            ? "border-destructive/20 bg-destructive/10 text-destructive"
                            : "border-border/60 bg-muted text-muted-foreground"
                        }`}
                        aria-label={`Status: ${project.status}`}
                      >
                        {project.status}
                      </span>
                    </div>

                    {project.description && (
                      <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                        {project.description}
                      </p>
                    )}

                    <div className="flex flex-wrap gap-2">
                      {project.domain && (
                        <span
                          className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium capitalize ${domainBadge(project.domain)}`}
                        >
                          {project.domain}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-1 text-xs text-muted-foreground pt-1 border-t border-border/40">
                      <Clock className="h-3 w-3" aria-hidden />
                      <time dateTime={project.updated_at}>{formatDate(project.updated_at)}</time>
                    </div>
                  </Link>

                  {/* Delete button */}
                  <div className="absolute right-3 top-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    {confirmDeleteId === project.id ? (
                      <div className="flex items-center gap-1">
                        <button
                          type="button"
                          onClick={() => handleDelete(project.id)}
                          disabled={deletingId === project.id}
                          aria-label="Confirm delete"
                          className="rounded-md bg-destructive px-2 py-1 text-xs font-medium text-white hover:bg-destructive/80 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
                        >
                          {deletingId === project.id ? "…" : "Delete"}
                        </button>
                        <button
                          type="button"
                          onClick={() => setConfirmDeleteId(null)}
                          aria-label="Cancel delete"
                          className="rounded-md border border-border bg-card px-2 py-1 text-xs text-muted-foreground hover:text-foreground transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          setConfirmDeleteId(project.id);
                        }}
                        aria-label={`Delete project ${project.name}`}
                        className="rounded-md border border-border/60 bg-card p-1.5 text-muted-foreground hover:border-destructive/40 hover:text-destructive transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                      >
                        <Trash2 className="h-3.5 w-3.5" aria-hidden />
                      </button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}

          {projects.length > 0 && (
            <p className="mt-6 text-center text-xs text-muted-foreground">
              {filtered.length} of {projects.length} project{projects.length !== 1 ? "s" : ""}
            </p>
          )}
        </>
      )}
    </main>
  );
}
