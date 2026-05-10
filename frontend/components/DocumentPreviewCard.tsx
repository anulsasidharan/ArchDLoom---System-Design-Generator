"use client";

import { FileText, GitBranch, Layers, Network, TrendingUp } from "lucide-react";

export type DocType = "prd" | "hld" | "lld" | "evolution" | "architecture";

const DOC_CONFIG: Record<
  DocType,
  {
    label: string;
    icon: React.ElementType;
    color: string;
    bg: string;
    border: string;
    sections: string[];
    format: string;
  }
> = {
  prd: {
    label: "PRD",
    icon: FileText,
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
    sections: ["Business Goals", "Functional Requirements", "NFRs", "Milestones", "Risk Assessment"],
    format: ".docx",
  },
  hld: {
    label: "HLD",
    icon: Network,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/20",
    sections: ["System Overview", "Component Breakdown", "Data Flow", "Security", "HA / DR"],
    format: ".docx",
  },
  lld: {
    label: "LLD",
    icon: Layers,
    color: "text-orange-400",
    bg: "bg-orange-500/10",
    border: "border-orange-500/20",
    sections: ["Database Schema", "Service Design", "Algorithms", "Error Handling", "Caching Strategy"],
    format: ".docx",
  },
  evolution: {
    label: "Evolution",
    icon: TrendingUp,
    color: "text-green-400",
    bg: "bg-green-500/10",
    border: "border-green-500/20",
    sections: ["MVP Phase", "Growth Phase", "Enterprise Phase", "Migration Paths", "Cost Analysis"],
    format: ".md",
  },
  architecture: {
    label: "Architecture",
    icon: GitBranch,
    color: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/20",
    sections: ["Component Map", "Trade-off Summary", "Selected Stack", "Diagrams", "Compliance Checklist"],
    format: ".md",
  },
};

type Props = {
  type: DocType;
  systemName?: string;
};

export function DocumentPreviewCard({ type, systemName }: Props) {
  const config = DOC_CONFIG[type];
  const Icon = config.icon;

  return (
    <article
      className={`card-hover rounded-xl border bg-card p-5 ${config.border}`}
      aria-label={`${config.label} document preview`}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border ${config.bg} ${config.border}`}>
          <Icon className={`h-4 w-4 ${config.color}`} aria-hidden />
        </div>
        <span className="rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
          {config.format}
        </span>
      </div>

      <div className="mb-3">
        <h3 className="text-sm font-semibold text-foreground">{config.label}</h3>
        {systemName && (
          <p className="text-xs text-muted-foreground truncate" title={systemName}>
            {systemName}
          </p>
        )}
      </div>

      <ul className="space-y-1" role="list" aria-label={`${config.label} sections`}>
        {config.sections.map((section) => (
          <li key={section} className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className={`h-1 w-1 shrink-0 rounded-full ${config.color.replace("text-", "bg-")}`} aria-hidden />
            {section}
          </li>
        ))}
      </ul>
    </article>
  );
}

export function DocumentPreviewGrid({
  systemName,
  selectedTypes,
}: {
  systemName?: string;
  selectedTypes?: Set<DocType>;
}) {
  const allTypes: DocType[] = ["prd", "hld", "lld", "evolution", "architecture"];
  const types = selectedTypes ? allTypes.filter((t) => selectedTypes.has(t)) : allTypes;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-medium text-foreground">Generated Documents</p>
        <span className="text-xs text-muted-foreground">{types.length} file{types.length !== 1 ? "s" : ""}</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {types.map((type) => (
          <DocumentPreviewCard key={type} type={type} systemName={systemName} />
        ))}
      </div>
    </div>
  );
}
