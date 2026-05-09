import Link from "next/link";
import {
  ArrowRight,
  Brain,
  FileText,
  GitBranch,
  Layers,
  Network,
  Shield,
  Sparkles,
  Zap,
  CheckCircle2,
} from "lucide-react";

const FEATURES = [
  {
    icon: Brain,
    title: "Natural Language Input",
    description:
      "Describe your system in plain English. Claude AI parses requirements, infers scale metrics, and identifies compliance needs automatically.",
  },
  {
    icon: Layers,
    title: "Real Component Icons",
    description:
      "Architecture diagrams with actual AWS, GCP, database, and AI/ML vendor icons — not generic boxes. Overlaid with Mermaid + SVG engine.",
  },
  {
    icon: GitBranch,
    title: "Trade-off Analysis",
    description:
      "Every component selection includes rationale, rejected alternatives with reasons, and accepted trade-offs in clear technical language.",
  },
  {
    icon: Sparkles,
    title: "AI/ML Specialization",
    description:
      "Native templates for RAG systems, fine-tuning pipelines, real-time inference, and agentic architectures with vector DB and LLM selections.",
  },
  {
    icon: Shield,
    title: "Enterprise Ready",
    description:
      "HA/DR strategies, GDPR/HIPAA/SOC 2 compliance sections, network security diagrams, and cost estimation built into every design.",
  },
  {
    icon: FileText,
    title: "5-Document Export",
    description:
      "Generates PRD, HLD, LLD, evolution roadmap, and architecture diagram — all exported as Word documents and Markdown in a single ZIP.",
  },
];

const STEPS = [
  {
    number: "01",
    title: "Describe Your System",
    description:
      "Write a natural language description of your system — users, scale, domain, tech preferences. The more detail, the better the output.",
  },
  {
    number: "02",
    title: "AI Generates Architecture",
    description:
      "Claude AI parses requirements, selects optimal components with trade-off analysis, and generates architecture diagrams in under 3 minutes.",
  },
  {
    number: "03",
    title: "Download & Iterate",
    description:
      "Download a ZIP with PRD, HLD, LLD, evolution plan, and diagrams. Review component decisions with full rationale and alternatives.",
  },
];

const STATS = [
  { value: "< 3 min", label: "Full documentation suite" },
  { value: "5 docs", label: "PRD · HLD · LLD · Diagrams" },
  { value: "100+", label: "Seeded tech components" },
];

export default function HomePage() {
  return (
    <main className="gradient-mesh">
      {/* Hero */}
      <section className="mx-auto max-w-7xl px-4 pb-20 pt-20 sm:px-6 sm:pt-28">
        <div className="mx-auto max-w-3xl text-center">
          <div className="animate-fade-in mb-6 inline-flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-3 py-1 text-xs font-medium text-green-400">
            <Zap className="h-3.5 w-3.5" aria-hidden />
            Powered by Claude AI · Enterprise Architecture Documentation
          </div>

          <h1 className="animate-slide-up text-balance text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Weaving Enterprise-Grade{" "}
            <span className="text-green-400">System Designs</span> with AI
          </h1>

          <p className="animate-slide-up-delay-1 mt-6 text-lg leading-relaxed text-muted-foreground sm:text-xl">
            Transform natural language requirements into production-ready PRD, HLD, LLD, and
            architecture diagrams — complete with component trade-offs and real vendor icons.
          </p>

          <div className="animate-slide-up-delay-2 mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/generate"
              className="inline-flex items-center gap-2 rounded-lg bg-green-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg transition hover:bg-green-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring glow-green"
            >
              Start Designing
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
            <Link
              href="/library"
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-6 py-3 text-sm font-semibold text-foreground transition hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              Browse Components
            </Link>
          </div>
        </div>

        {/* Hero diagram preview */}
        <div className="mt-16 overflow-hidden rounded-2xl border border-border/60 bg-card/50 shadow-2xl">
          <div className="flex items-center gap-1.5 border-b border-border/60 bg-muted/30 px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-red-500/70" />
            <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
            <span className="h-3 w-3 rounded-full bg-green-500/70" />
            <span className="ml-3 text-xs text-muted-foreground">architecture-preview.svg</span>
          </div>
          <div className="flex min-h-[220px] items-center justify-center p-8 sm:min-h-[280px]">
            <div className="w-full max-w-2xl">
              <div className="grid grid-cols-3 gap-3 text-center sm:grid-cols-5">
                {["API Gateway", "App Service", "PostgreSQL", "Redis Cache", "Vector DB"].map((name) => (
                  <div
                    key={name}
                    className="flex flex-col items-center gap-2 rounded-xl border border-border/60 bg-muted/30 p-3"
                  >
                    <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-green-500/20 to-blue-500/20 border border-border/40" />
                    <span className="text-xs text-muted-foreground leading-tight">{name}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-center gap-2">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-green-500/40 to-transparent" />
                <span className="text-xs text-green-400 font-medium">Real component icons in generated diagrams</span>
                <div className="h-px flex-1 bg-gradient-to-r from-green-500/40 via-transparent to-transparent" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border/60 bg-muted/20">
        <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6">
          <dl className="grid grid-cols-1 gap-8 sm:grid-cols-3">
            {STATS.map((stat) => (
              <div key={stat.label} className="flex flex-col items-center gap-1 text-center">
                <dt className="text-3xl font-bold tabular-nums text-green-400">{stat.value}</dt>
                <dd className="text-sm text-muted-foreground">{stat.label}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold tracking-tight">
            Everything a solutions architect needs
          </h2>
          <p className="mt-3 text-muted-foreground">
            From requirement parsing to enterprise documentation in one workflow.
          </p>
        </div>

        <ul className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3" role="list">
          {FEATURES.map((feature) => {
            const Icon = feature.icon;
            return (
              <li
                key={feature.title}
                className="card-hover rounded-xl border border-border/60 bg-card p-6"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10 border border-green-500/20">
                  <Icon className="h-5 w-5 text-green-400" aria-hidden />
                </div>
                <h3 className="mb-2 font-semibold text-foreground">{feature.title}</h3>
                <p className="text-sm leading-relaxed text-muted-foreground">{feature.description}</p>
              </li>
            );
          })}
        </ul>
      </section>

      {/* How It Works */}
      <section className="border-y border-border/60 bg-muted/20">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold tracking-tight">How it works</h2>
            <p className="mt-3 text-muted-foreground">
              Three steps from requirement to production-ready documentation.
            </p>
          </div>

          <ol className="grid gap-8 sm:grid-cols-3" role="list">
            {STEPS.map((step, i) => (
              <li key={step.number} className="relative flex flex-col gap-4">
                {i < STEPS.length - 1 && (
                  <div className="absolute left-12 top-6 hidden h-px w-[calc(100%+2rem)] bg-gradient-to-r from-green-500/30 to-transparent sm:block" aria-hidden />
                )}
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-500/10 border border-green-500/30">
                  <span className="text-sm font-bold tabular-nums text-green-400">{step.number}</span>
                </div>
                <div>
                  <h3 className="mb-2 font-semibold text-foreground">{step.title}</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">{step.description}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* What you get */}
      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <div className="grid gap-8 lg:grid-cols-2 lg:gap-12 lg:items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">
              Complete documentation suite
            </h2>
            <p className="mt-4 text-muted-foreground leading-relaxed">
              Every generation produces five production-ready documents tailored to your system
              requirements, with AI-selected components and full trade-off analysis.
            </p>
            <ul className="mt-6 space-y-3" role="list">
              {[
                "Product Requirements Document (PRD) with user stories",
                "High-Level Design (HLD) with component rationale",
                "Low-Level Design (LLD) with schema and algorithms",
                "System evolution roadmap (MVP → Enterprise)",
                "Architecture diagrams with real vendor icons",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-400" aria-hidden />
                  {item}
                </li>
              ))}
            </ul>
            <div className="mt-8">
              <Link
                href="/generate"
                className="inline-flex items-center gap-2 rounded-lg bg-green-500 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-green-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                Generate your design
                <ArrowRight className="h-4 w-4" aria-hidden />
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {[
              { label: "PRD", desc: "Product Requirements", color: "blue" },
              { label: "HLD", desc: "High-Level Design", color: "purple" },
              { label: "LLD", desc: "Low-Level Design", color: "orange" },
              { label: "Evolution", desc: "MVP → Enterprise", color: "green" },
              { label: "Architecture", desc: "Diagram + Icons", color: "green" },
              { label: "ZIP Export", desc: "All files bundled", color: "slate" },
            ].map((doc) => (
              <div
                key={doc.label}
                className="rounded-xl border border-border/60 bg-card p-4 card-hover"
              >
                <div className="mb-1 flex items-center gap-2">
                  <Network className="h-4 w-4 text-muted-foreground" aria-hidden />
                  <span className="text-xs font-semibold text-foreground">{doc.label}</span>
                </div>
                <p className="text-xs text-muted-foreground">{doc.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-border/60 bg-muted/20">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight">
            Ready to design your next system?
          </h2>
          <p className="mt-4 text-muted-foreground max-w-xl mx-auto">
            Describe your requirements and get a complete, enterprise-grade architecture
            documentation suite in under 3 minutes.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/generate"
              className="inline-flex items-center gap-2 rounded-lg bg-green-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg transition hover:bg-green-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring glow-green"
            >
              Start Designing Free
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
            <Link
              href="/projects"
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-6 py-3 text-sm font-semibold text-foreground transition hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              View Projects
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/60">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Layers className="h-4 w-4 text-green-400" aria-hidden />
            <span className="font-medium text-foreground">ArchDLoom</span>
            <span>— AI System Design Generator</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Powered by Anthropic Claude · Built with Next.js 14
          </p>
        </div>
      </footer>
    </main>
  );
}
