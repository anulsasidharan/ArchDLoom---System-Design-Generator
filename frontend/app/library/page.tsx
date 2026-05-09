"use client";

import { useEffect, useMemo, useState } from "react";
import { Search, Database, ChevronRight, AlertCircle, CheckCircle2, X, Filter } from "lucide-react";

type Component = {
  id: string;
  name: string;
  category: string;
  vendor?: string | null;
  icon_url?: string | null;
  features?: string[];
  trade_offs?: { pros: string[]; cons: string[] } | null;
  pricing_model?: string | null;
  base_cost_usd?: number | null;
  selection_criteria?: Record<string, string> | null;
  docs_url?: string | null;
};

const CATEGORY_LABELS: Record<string, string> = {
  all: "All",
  database: "Databases",
  cache: "Cache",
  message_queue: "Message Queues",
  compute: "Compute",
  llm_provider: "LLM Providers",
  vector_database: "Vector DBs",
  embedding_model: "Embeddings",
  monitoring: "Monitoring",
  api_gateway: "API Gateways",
  storage: "Storage",
  cdn: "CDN",
};

const CATEGORY_COLORS: Record<string, string> = {
  database: "text-blue-400 bg-blue-400/10 border-blue-400/20",
  cache: "text-red-400 bg-red-400/10 border-red-400/20",
  message_queue: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
  compute: "text-purple-400 bg-purple-400/10 border-purple-400/20",
  llm_provider: "text-green-400 bg-green-400/10 border-green-400/20",
  vector_database: "text-cyan-400 bg-cyan-400/10 border-cyan-400/20",
  embedding_model: "text-pink-400 bg-pink-400/10 border-pink-400/20",
  monitoring: "text-orange-400 bg-orange-400/10 border-orange-400/20",
  api_gateway: "text-indigo-400 bg-indigo-400/10 border-indigo-400/20",
  storage: "text-teal-400 bg-teal-400/10 border-teal-400/20",
  cdn: "text-lime-400 bg-lime-400/10 border-lime-400/20",
};

function categoryBadge(cat: string) {
  return CATEGORY_COLORS[cat] ?? "text-muted-foreground bg-muted border-border/60";
}

type SelectedComponent = Component;

export default function LibraryPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const base = `${apiUrl}/api/v1`;

  const [components, setComponents] = useState<Component[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState("all");
  const [selected, setSelected] = useState<SelectedComponent | null>(null);

  const fetchComponents = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (activeCategory !== "all") params.set("category", activeCategory);
      if (search) params.set("search", search);

      const res = await fetch(`${base}/components?${params}`);
      if (!res.ok) throw new Error(`Failed to load components (${res.status})`);
      const data = (await res.json()) as Component[];
      setComponents(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load component library");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchComponents();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCategory]);

  const filtered = useMemo(() => {
    if (!search) return components;
    const q = search.toLowerCase();
    return components.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.vendor ?? "").toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q) ||
        (c.features ?? []).some((f) => f.toLowerCase().includes(q)),
    );
  }, [components, search]);

  const categories = useMemo(() => {
    const cats = new Set(components.map((c) => c.category));
    return ["all", ...Array.from(cats).sort()];
  }, [components]);

  return (
    <main className="mx-auto min-h-dvh max-w-7xl px-4 py-10 sm:px-6">
      {/* Header */}
      <div className="mb-8 animate-fade-in">
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
          <span>ArchDLoom</span>
          <ChevronRight className="h-3 w-3" aria-hidden />
          <span className="text-foreground">Component Library</span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">Component Library</h1>
        <p className="mt-1 text-sm text-muted-foreground max-w-2xl">
          Browse all technology components available for selection during architecture generation.
          Each component includes trade-offs, costs, and selection criteria.
        </p>
      </div>

      {/* Search + filter bar */}
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground pointer-events-none" aria-hidden />
          <input
            type="search"
            placeholder="Search by name, vendor, or feature…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search components"
            className="w-full rounded-lg border border-input bg-muted/30 py-2.5 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground/60 outline-none focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring transition"
          />
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Filter className="h-3.5 w-3.5" aria-hidden />
          <span className="font-medium text-foreground">{filtered.length}</span>
          <span>components</span>
        </div>
      </div>

      {/* Category tabs */}
      <div
        className="mb-6 flex flex-wrap gap-2"
        role="tablist"
        aria-label="Filter by category"
      >
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            role="tab"
            aria-selected={activeCategory === cat}
            onClick={() => setActiveCategory(cat)}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
              activeCategory === cat
                ? cat === "all"
                  ? "border-green-500/40 bg-green-500/10 text-green-400"
                  : `${categoryBadge(cat)}`
                : "border-border/60 bg-muted/20 text-muted-foreground hover:border-border hover:text-foreground"
            }`}
          >
            {CATEGORY_LABELS[cat] ?? cat.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3" role="alert">
          <AlertCircle className="h-4 w-4 shrink-0 text-destructive mt-0.5" aria-hidden />
          <div className="flex-1">
            <p className="text-sm text-destructive font-medium">Failed to load components</p>
            <p className="text-xs text-muted-foreground mt-0.5">{error}</p>
          </div>
          <button
            onClick={fetchComponents}
            className="rounded-md px-3 py-1 text-xs border border-border text-foreground hover:bg-muted transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Retry
          </button>
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" aria-label="Loading" role="list">
          {Array.from({ length: 12 }).map((_, i) => (
            <li key={i} className="rounded-xl border border-border/60 bg-card p-5 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <div className="skeleton h-9 w-9 rounded-lg" />
                <div className="skeleton h-5 w-16 rounded-full" />
              </div>
              <div className="skeleton h-4 w-28 rounded" />
              <div className="skeleton h-3 w-20 rounded" />
              <div className="flex gap-1.5 flex-wrap">
                <div className="skeleton h-5 w-14 rounded-full" />
                <div className="skeleton h-5 w-18 rounded-full" />
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Component grid */}
      {!loading && !error && (
        <>
          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20 text-center">
              <Database className="h-12 w-12 text-muted-foreground/40 mb-4" aria-hidden />
              <p className="text-sm font-medium text-muted-foreground">No components found</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {search ? "Try different keywords" : "The component library is empty"}
              </p>
            </div>
          ) : (
            <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" role="list">
              {filtered.map((comp) => (
                <li key={comp.id}>
                  <button
                    type="button"
                    onClick={() => setSelected(selected?.id === comp.id ? null : comp)}
                    aria-pressed={selected?.id === comp.id}
                    className={`card-hover w-full rounded-xl border p-5 text-left space-y-3 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                      selected?.id === comp.id
                        ? "border-green-500/40 bg-green-500/5"
                        : "border-border/60 bg-card"
                    }`}
                  >
                    {/* Icon + category */}
                    <div className="flex items-start justify-between gap-2">
                      {comp.icon_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          src={comp.icon_url}
                          alt=""
                          className="h-9 w-9 rounded-lg border border-border/40 bg-muted object-contain p-1"
                        />
                      ) : (
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border/40 bg-muted text-xs font-bold text-muted-foreground">
                          {comp.name.slice(0, 2).toUpperCase()}
                        </div>
                      )}
                      <span
                        className={`rounded-full border px-2 py-0.5 text-xs font-medium capitalize shrink-0 ${categoryBadge(comp.category)}`}
                      >
                        {CATEGORY_LABELS[comp.category] ?? comp.category.replace(/_/g, " ")}
                      </span>
                    </div>

                    {/* Name + vendor */}
                    <div>
                      <p className="text-sm font-semibold text-foreground leading-tight">{comp.name}</p>
                      {comp.vendor && (
                        <p className="text-xs text-muted-foreground mt-0.5">{comp.vendor}</p>
                      )}
                    </div>

                    {/* Cost */}
                    {comp.base_cost_usd != null && (
                      <p className="text-xs tabular-nums text-green-400 font-medium">
                        ${comp.base_cost_usd.toLocaleString()}/mo base
                      </p>
                    )}

                    {/* Features */}
                    {comp.features && comp.features.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {comp.features.slice(0, 3).map((f) => (
                          <span
                            key={f}
                            className="rounded-full border border-border/40 bg-muted/30 px-2 py-0.5 text-xs text-muted-foreground"
                          >
                            {f}
                          </span>
                        ))}
                        {comp.features.length > 3 && (
                          <span className="text-xs text-muted-foreground">
                            +{comp.features.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}

      {/* Component detail drawer */}
      {selected && (
        <aside
          className="fixed inset-y-0 right-0 z-50 flex w-full max-w-sm flex-col border-l border-border/60 bg-background/95 shadow-2xl backdrop-blur-md animate-fade-in overflow-y-auto"
          aria-label="Component details"
        >
          <div className="sticky top-0 z-10 flex items-start justify-between gap-3 border-b border-border/60 bg-background/95 px-6 py-5 backdrop-blur-sm">
            <div className="flex items-center gap-3 min-w-0">
              {selected.icon_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={selected.icon_url}
                  alt=""
                  className="h-10 w-10 shrink-0 rounded-lg border border-border/40 bg-muted object-contain p-1"
                />
              ) : (
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border/40 bg-muted text-sm font-bold text-muted-foreground">
                  {selected.name.slice(0, 2).toUpperCase()}
                </div>
              )}
              <div className="min-w-0">
                <p className="text-xs text-muted-foreground capitalize">
                  {CATEGORY_LABELS[selected.category] ?? selected.category}
                </p>
                <h2 className="text-base font-semibold text-foreground truncate">{selected.name}</h2>
                {selected.vendor && (
                  <p className="text-xs text-muted-foreground">{selected.vendor}</p>
                )}
              </div>
            </div>
            <button
              type="button"
              onClick={() => setSelected(null)}
              aria-label="Close component details"
              className="shrink-0 rounded-md p-1.5 text-muted-foreground transition hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <X className="h-5 w-5" aria-hidden />
            </button>
          </div>

          <div className="flex-1 space-y-6 px-6 py-5">
            {/* Pricing */}
            {(selected.base_cost_usd != null || selected.pricing_model) && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Pricing</p>
                <div className="rounded-lg border border-border/60 bg-muted/20 px-4 py-3">
                  {selected.base_cost_usd != null && (
                    <p className="text-2xl font-bold tabular-nums text-green-400">
                      ${selected.base_cost_usd.toLocaleString()}
                      <span className="text-sm font-normal text-muted-foreground">/mo base</span>
                    </p>
                  )}
                  {selected.pricing_model && (
                    <p className="text-xs text-muted-foreground capitalize mt-0.5">
                      Model: {selected.pricing_model.replace(/_/g, " ")}
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Selection criteria */}
            {selected.selection_criteria && Object.keys(selected.selection_criteria).length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Best For</p>
                <dl className="space-y-2">
                  {Object.entries(selected.selection_criteria).map(([k, v]) => (
                    <div key={k} className="text-xs">
                      <dt className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</dt>
                      <dd className="text-foreground">{String(v)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            {/* Features */}
            {selected.features && selected.features.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Features</p>
                <ul className="space-y-1.5" role="list">
                  {selected.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-xs text-muted-foreground">
                      <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-green-400" aria-hidden />
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Trade-offs */}
            {selected.trade_offs && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Trade-offs</p>
                <div className="space-y-3">
                  {selected.trade_offs.pros.length > 0 && (
                    <div>
                      <p className="mb-1 text-xs font-medium text-green-400">Advantages</p>
                      <ul className="space-y-1" role="list">
                        {selected.trade_offs.pros.map((p) => (
                          <li key={p} className="flex items-start gap-2 text-xs text-muted-foreground">
                            <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-green-400" aria-hidden />
                            {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selected.trade_offs.cons.length > 0 && (
                    <div>
                      <p className="mb-1 text-xs font-medium text-amber-400">Limitations</p>
                      <ul className="space-y-1" role="list">
                        {selected.trade_offs.cons.map((c) => (
                          <li key={c} className="flex items-start gap-2 text-xs text-muted-foreground">
                            <span className="mt-0.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" aria-hidden />
                            {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Docs link */}
            {selected.docs_url && (
              <a
                href={selected.docs_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 rounded-lg border border-border/60 bg-muted/20 px-4 py-2.5 text-sm text-muted-foreground transition hover:border-border hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                View Documentation
                <ChevronRight className="h-4 w-4" aria-hidden />
              </a>
            )}
          </div>
        </aside>
      )}

      {/* Overlay when drawer open */}
      {selected && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
          onClick={() => setSelected(null)}
          aria-hidden
        />
      )}
    </main>
  );
}
